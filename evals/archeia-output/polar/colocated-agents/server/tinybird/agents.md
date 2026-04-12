## Local Rules

- Files in this directory are Tinybird configuration, not Python modules. Do not add Python code here.
- `datasources/` defines event schemas. `pipes/` defines transformations. `endpoints/` defines query APIs.
- Deploy changes with `uv run task tb_deploy` from `server/`.
- Changes to datasource schemas may require migration coordination with Tinybird.
- Do not edit generated files; modify the source definitions and redeploy.

## README Maintenance

Before working in this directory, read the README.md.
After completing work, update the README's Learnings section with anything non-obvious you discovered.

Maintains: server/tinybird/README.md
