from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evals.analysis.aggregate import pairwise_condition_comparison, wilcoxon_signed_rank
from evals.collectors.metrics import collect_metrics
from evals.harness.condition_applier import apply_condition


class ConditionApplierTests(unittest.TestCase):
    def test_apply_condition_replaces_docs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            worktree = root / "worktree"
            archeia_output = root / "bundle"
            config_path = root / "conditions.yaml"

            (worktree / ".archeia").mkdir(parents=True)
            (worktree / ".archeia" / "Old.md").write_text("old", encoding="utf-8")
            (worktree / "AGENTS.md").write_text("old agents", encoding="utf-8")
            (worktree / "src").mkdir(parents=True)
            (worktree / "src" / "README.md").write_text("old readme", encoding="utf-8")

            (archeia_output / ".archeia").mkdir(parents=True)
            (archeia_output / ".archeia" / "Architecture.md").write_text("new arch", encoding="utf-8")
            (archeia_output / "AGENTS.md").write_text("new agents", encoding="utf-8")
            (archeia_output / "CLAUDE.md").write_text("new claude", encoding="utf-8")
            (archeia_output / "colocated-readmes" / "src").mkdir(parents=True)
            (archeia_output / "colocated-readmes" / "src" / "README.md").write_text(
                "new readme", encoding="utf-8"
            )

            config = {
                "doc_sets": {
                    "root_docs": ["AGENTS.md", "CLAUDE.md"],
                    "archeia": [".archeia"],
                    "colocated_readmes": ["colocated-readmes"],
                },
                "conditions": [
                    {
                        "id": "l2",
                        "repo_ids": ["*"],
                        "keep_existing_docs": False,
                        "include_sets": ["root_docs", "archeia", "colocated_readmes", "colocated_agents"],
                    }
                ],
            }
            config_path.write_text(json.dumps(config), encoding="utf-8")

            summary = apply_condition(
                repo_id="demo",
                condition_id="l2",
                worktree=worktree,
                archeia_output=archeia_output,
                conditions_path=config_path,
            )

            self.assertIn("AGENTS.md", summary["copied_paths"])
            self.assertTrue((worktree / ".archeia" / "Architecture.md").exists())
            self.assertEqual((worktree / "src" / "README.md").read_text(encoding="utf-8"), "new readme")

    def test_keep_existing_docs_preserves_native_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            worktree = root / "worktree"
            archeia_output = root / "bundle"
            config_path = root / "conditions.yaml"

            worktree.mkdir(parents=True)
            (worktree / "AGENTS.md").write_text("native agents", encoding="utf-8")
            (worktree / "CLAUDE.md").write_text("native claude", encoding="utf-8")
            (worktree / "ARCHITECTURE.md").write_text("native architecture", encoding="utf-8")

            archeia_output.mkdir(parents=True)
            (archeia_output / "AGENTS.md").write_text("generated agents", encoding="utf-8")
            (archeia_output / "CLAUDE.md").write_text("generated claude", encoding="utf-8")

            config = {
                "doc_sets": {
                    "root_docs": ["AGENTS.md", "CLAUDE.md"],
                    "archeia": [".archeia"],
                },
                "conditions": [
                    {
                        "id": "l0",
                        "repo_ids": ["*"],
                        "keep_existing_docs": True,
                        "include_sets": [],
                    }
                ],
            }
            config_path.write_text(json.dumps(config), encoding="utf-8")

            summary = apply_condition(
                repo_id="demo",
                condition_id="l0",
                worktree=worktree,
                archeia_output=archeia_output,
                conditions_path=config_path,
            )

            self.assertTrue(summary["kept_existing_docs"])
            self.assertEqual(summary["removed_paths"], [])
            self.assertEqual(summary["copied_paths"], [])
            self.assertEqual((worktree / "AGENTS.md").read_text(encoding="utf-8"), "native agents")
            self.assertEqual((worktree / "CLAUDE.md").read_text(encoding="utf-8"), "native claude")
            self.assertEqual(
                (worktree / "ARCHITECTURE.md").read_text(encoding="utf-8"),
                "native architecture",
            )


class MetricsCollectorTests(unittest.TestCase):
    def test_collect_metrics_from_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            transcript = Path(temp_dir) / "conversation.jsonl"
            transcript.write_text(
                "\n".join(
                    [
                        json.dumps({"timestamp": "2026-04-09T00:00:00+00:00", "tool_name": "Read"}),
                        json.dumps({"timestamp": "2026-04-09T00:00:05+00:00", "tool_name": "Edit"}),
                        json.dumps(
                            {
                                "timestamp": "2026-04-09T00:00:20+00:00",
                                "usage": {"input_tokens": 50, "output_tokens": 10, "total_tokens": 60},
                            }
                        ),
                    ]
                ),
                encoding="utf-8",
            )

            payload = collect_metrics(transcript)
            self.assertEqual(payload["tool_call_count"], 2)
            self.assertEqual(payload["total_tokens"], 60)
            self.assertEqual(payload["time_to_first_edit_seconds"], 5.0)
            self.assertEqual(payload["time_to_completion_seconds"], 20.0)


class AggregateTests(unittest.TestCase):
    def test_wilcoxon_signed_rank_handles_pairs(self) -> None:
        payload = wilcoxon_signed_rank([1.0, 2.0, -0.5, 1.5])
        self.assertEqual(payload["count"], 4)
        self.assertIn("p_value", payload)

    def test_pairwise_condition_comparison_pairs_by_repo_task_trial(self) -> None:
        results = [
            {
                "repo_id": "arq",
                "trial": 1,
                "condition_id": "l0",
                "task": {"id": "t1"},
                "judge": {"total_score": 70},
            },
            {
                "repo_id": "arq",
                "trial": 1,
                "condition_id": "l2",
                "task": {"id": "t1"},
                "judge": {"total_score": 80},
            },
        ]

        payload = pairwise_condition_comparison(results, "judge.total_score", "l0", "l2")
        self.assertEqual(payload["pair_count"], 1)
        self.assertEqual(payload["mean_difference"], 10.0)


if __name__ == "__main__":
    unittest.main()
