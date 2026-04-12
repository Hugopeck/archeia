from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))

from evals.common import confidence_interval_95, mean, metric_value, sample_stddev, utc_now, write_json


DEFAULT_METRICS = [
    "judge.total_score",
    "metrics.total_tokens",
    "metrics.tool_call_count",
    "metrics.exploration_to_action_ratio",
    "metrics.time_to_first_edit_seconds",
    "metrics.time_to_completion_seconds",
    "code_quality.lint_delta",
]


def load_results(results_root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in sorted(results_root.rglob("*.json")):
        results.append(json.loads(path.read_text(encoding="utf-8")))
    return results


def metric_summary(results: list[dict[str, Any]], metric_path: str) -> dict[str, Any]:
    values = [value for item in results if (value := metric_value(item, metric_path)) is not None]
    ci = confidence_interval_95(values)
    return {
        "metric": metric_path,
        "count": len(values),
        "mean": ci["mean"] if ci else None,
        "ci95_lower": ci["lower"] if ci else None,
        "ci95_upper": ci["upper"] if ci else None,
        "stddev": sample_stddev(values),
        "min": min(values) if values else None,
        "max": max(values) if values else None,
    }


def group_by(results: list[dict[str, Any]], key_path: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in results:
        value = metric_value(item, key_path)
        if value is None:
            current: Any = item
            for segment in key_path.split("."):
                if not isinstance(current, dict):
                    current = None
                    break
                current = current.get(segment)
            value = current
        key = str(value)
        grouped.setdefault(key, []).append(item)
    return grouped


def normal_cdf(value: float) -> float:
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def wilcoxon_signed_rank(paired_differences: list[float]) -> dict[str, Any]:
    non_zero = [value for value in paired_differences if value != 0]
    if not non_zero:
        return {"count": 0, "w_plus": 0.0, "w_minus": 0.0, "p_value": None}

    ranked = sorted((abs(value), value) for value in non_zero)
    ranks: list[tuple[float, float]] = []
    index = 0
    while index < len(ranked):
        tie_end = index
        while tie_end < len(ranked) and ranked[tie_end][0] == ranked[index][0]:
            tie_end += 1
        average_rank = (index + 1 + tie_end) / 2
        for item in ranked[index:tie_end]:
            ranks.append((average_rank, item[1]))
        index = tie_end

    w_plus = sum(rank for rank, diff in ranks if diff > 0)
    w_minus = sum(rank for rank, diff in ranks if diff < 0)
    n = len(ranks)
    mean_rank = n * (n + 1) / 4
    variance = n * (n + 1) * (2 * n + 1) / 24
    if variance == 0:
        p_value = None
    else:
        z = (min(w_plus, w_minus) - mean_rank) / math.sqrt(variance)
        p_value = 2 * normal_cdf(z)
    return {
        "count": n,
        "w_plus": w_plus,
        "w_minus": w_minus,
        "p_value": p_value,
    }


def pair_key(item: dict[str, Any]) -> str:
    task = item.get("task", {}) if isinstance(item.get("task"), dict) else {}
    return "::".join(
        [
            str(item.get("repo_id")),
            str(task.get("id")),
            str(item.get("trial")),
        ]
    )


def pairwise_condition_comparison(results: list[dict[str, Any]], metric_path: str, left: str, right: str) -> dict[str, Any]:
    left_items = {pair_key(item): item for item in results if item.get("condition_id") == left}
    right_items = {pair_key(item): item for item in results if item.get("condition_id") == right}
    paired_diffs: list[float] = []
    for key in sorted(set(left_items) & set(right_items)):
        left_metric = metric_value(left_items[key], metric_path)
        right_metric = metric_value(right_items[key], metric_path)
        if left_metric is None or right_metric is None:
            continue
        paired_diffs.append(right_metric - left_metric)

    return {
        "metric": metric_path,
        "left_condition": left,
        "right_condition": right,
        "pair_count": len(paired_diffs),
        "mean_difference": mean(paired_diffs),
        "wilcoxon": wilcoxon_signed_rank(paired_diffs),
    }


def aggregate_results(results_root: Path, metrics: list[str]) -> dict[str, Any]:
    results = load_results(results_root)
    by_condition = group_by(results, "condition_id")
    by_repo = group_by(results, "repo_id")
    by_category = group_by(results, "task.category")

    payload = {
        "generated_at": utc_now(),
        "results_root": str(results_root),
        "result_count": len(results),
        "metrics": metrics,
        "overall": {metric: metric_summary(results, metric) for metric in metrics},
        "by_condition": {
            condition: {metric: metric_summary(items, metric) for metric in metrics}
            for condition, items in by_condition.items()
        },
        "by_repo": {
            repo: {metric: metric_summary(items, metric) for metric in metrics}
            for repo, items in by_repo.items()
        },
        "by_category": {
            category: {metric: metric_summary(items, metric) for metric in metrics}
            for category, items in by_category.items()
        },
        "pairwise": [
            pairwise_condition_comparison(results, "judge.total_score", "l0", "l1"),
            pairwise_condition_comparison(results, "judge.total_score", "l0", "l2"),
            pairwise_condition_comparison(results, "metrics.total_tokens", "l0", "l1"),
            pairwise_condition_comparison(results, "metrics.total_tokens", "l0", "l2"),
        ],
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate raw Archeia eval results")
    parser.add_argument("--results-root", default="evals/results/raw")
    parser.add_argument("--output", default="evals/results/reports/aggregate.json")
    parser.add_argument("--metric", action="append", dest="metrics")
    args = parser.parse_args()

    metrics = args.metrics or DEFAULT_METRICS
    payload = aggregate_results(Path(args.results_root), metrics)
    write_json(Path(args.output), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
