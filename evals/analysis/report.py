from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))


def format_number(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def metric_table(section: dict[str, Any], metrics: list[str]) -> list[str]:
    lines = ["| Metric | N | Mean | 95% CI |", "|---|---:|---:|---:|"]
    for metric in metrics:
        item = section.get(metric, {})
        ci = f"{format_number(item.get('ci95_lower'))} to {format_number(item.get('ci95_upper'))}"
        lines.append(
            f"| `{metric}` | {format_number(item.get('count'))} | {format_number(item.get('mean'))} | {ci} |"
        )
    return lines


def render_report(aggregate: dict[str, Any]) -> str:
    metrics = aggregate.get("metrics", [])
    lines = [
        "# Archeia Evaluation Report",
        "",
        f"Generated at: `{aggregate.get('generated_at')}`",
        f"Result count: **{aggregate.get('result_count', 0)}**",
        "",
        "## Overall",
        "",
        *metric_table(aggregate.get("overall", {}), metrics),
        "",
        "## By Condition",
        "",
    ]

    for condition, section in sorted(aggregate.get("by_condition", {}).items()):
        lines.extend([f"### {condition}", "", *metric_table(section, metrics), ""])

    lines.extend(["## Pairwise", ""])
    lines.append("| Comparison | Pairs | Mean Δ | p-value |")
    lines.append("|---|---:|---:|---:|")
    for item in aggregate.get("pairwise", []):
        wilcoxon = item.get("wilcoxon", {})
        comparison = f"`{item.get('left_condition')}` → `{item.get('right_condition')}` / `{item.get('metric')}`"
        lines.append(
            f"| {comparison} | {format_number(item.get('pair_count'))} | {format_number(item.get('mean_difference'))} | {format_number(wilcoxon.get('p_value'))} |"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a markdown report from aggregate results")
    parser.add_argument("--aggregate", default="evals/results/reports/aggregate.json")
    parser.add_argument("--output", default="evals/results/reports/report.md")
    args = parser.parse_args()

    aggregate = json.loads(Path(args.aggregate).read_text(encoding="utf-8"))
    report = render_report(aggregate)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
