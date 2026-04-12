## contrib — Local Agent Instructions

- Do not modify any file in this directory. All contents are vendored third-party code.
- Do not run ruff, mypy, or any linter on files in `contrib/`. The `pyproject.toml` excludes this directory from all linting and type-checking. The ruff `extend-exclude` and mypy `overrides` configs reflect this intentionally.
- Do not add new files here unless explicitly vendoring an external dependency with maintainer approval.
- If a vendored library needs to be updated, replace the entire vendor snapshot — do not apply partial patches.

## README Maintenance

Before working in this directory, read `mitmproxy/contrib/README.md`.
After completing work, update the README's Learnings section with anything non-obvious discovered.

Maintains: `mitmproxy/contrib/README.md`
