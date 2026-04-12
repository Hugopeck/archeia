## Local Rules

- New benefit types require a strategy in `strategies/`. Register them in `registry.py`.
- Each strategy must implement grant, revoke, and validate methods from the base strategy interface.
- Benefit grants are created asynchronously via worker tasks, not synchronously in the request path.
- The `grant/` subdirectory manages grant lifecycle (creation, revocation, status tracking).
- Do not add benefit-specific logic to `service.py`; delegate to the appropriate strategy.

## README Maintenance

Before working in this directory, read the README.md.
After completing work, update the README's Learnings section with anything non-obvious you discovered.

Maintains: server/polar/benefit/README.md
