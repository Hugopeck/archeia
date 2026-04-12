import json
import subprocess
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent
FIXTURES_DIR = TESTS_DIR / "fixtures"
DISCOVER = SCRIPTS_DIR / "discover.sh"
VALIDATE = SCRIPTS_DIR / "validate-evidence.sh"
VALIDATE_FALLBACK = SCRIPTS_DIR / "validate_evidence_fallback.sh"


class ScriptTests(unittest.TestCase):
    maxDiff = None

    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, text=True, capture_output=True, check=False)

    def test_discover_returns_expected_structure(self) -> None:
        repo = FIXTURES_DIR / "discover_repo"
        result = self.run_cmd(str(DISCOVER), str(repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["repo_root"], str(repo.resolve()))
        self.assertIn("package.json", payload["files_to_read"])
        self.assertIn("README.md", payload["files_to_read"])
        self.assertIn("Dockerfile", payload["by_priority"]["root_configs"])
        self.assertIn("tests/conftest.py", payload["by_priority"]["test_setup"])
        self.assertIn("src", payload["source_roots"])
        self.assertIn("apps/web/src", payload["source_roots"])
        self.assertIn("packages/shared/src", payload["source_roots"])
        self.assertIn("src/index.ts", payload["by_priority"]["source_samples"])
        self.assertTrue(payload["signals"]["has_workspaces"])
        self.assertTrue(payload["signals"]["has_docker"])
        self.assertTrue(payload["signals"]["has_tests"])

    def test_wrapper_validates_clean_fixture_and_root_docs(self) -> None:
        repo = FIXTURES_DIR / "validator_clean"
        output_dir = repo / ".archeia"
        result = self.run_cmd(
            str(VALIDATE),
            str(repo),
            str(output_dir),
            "--include-root-docs",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("mode=python", result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["mode"], "python")
        self.assertIn(".archeia/codebase/architecture/architecture.md", payload["checked_files"])
        self.assertIn("AGENTS.md", payload["checked_files"])
        self.assertEqual(payload["invalid_paths"], [])
        self.assertEqual(payload["malformed_evidence"], [])

    def test_wrapper_reports_invalid_and_malformed_evidence(self) -> None:
        repo = FIXTURES_DIR / "validator_invalid"
        output_dir = repo / ".archeia"
        result = self.run_cmd(str(VALIDATE), str(repo), str(output_dir))
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)

        self.assertIn("missing.ts", payload["invalid_paths"])
        self.assertTrue(
            any(item["reason"] == "placeholder token" for item in payload["malformed_evidence"]),
            payload,
        )

    def test_fallback_validator_reports_findings(self) -> None:
        repo = FIXTURES_DIR / "validator_invalid"
        output_dir = repo / ".archeia"
        result = self.run_cmd(str(VALIDATE_FALLBACK), str(repo), str(output_dir))
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["mode"], "fallback")
        self.assertIn("missing.ts", payload["invalid_paths"])
        self.assertTrue(
            any(item["reason"] == "placeholder token" for item in payload["malformed_evidence"]),
            payload,
        )


if __name__ == "__main__":
    unittest.main()
