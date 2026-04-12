# tests

Backend test suite for the Polar API server. Mirrors the `server/polar/` module structure. Uses pytest with asyncio strict mode and class-based test organization.

## Structure

```mermaid
graph LR
    FIXTURES[fixtures/] -->|provides| TESTS[test modules]
    TESTS -->|mirrors| POLAR[polar/{module}/]
    CONFTEST[conftest.py] -->|session, factories| TESTS
```

## Key Concepts

- **Mirror structure** -- `tests/foo/test_endpoints.py` tests `polar/foo/endpoints.py`. One test class per method, each test case is a different scenario.
- **Fixtures** -- `fixtures/` provides reusable test data factories. `conftest.py` configures `SaveFixture`, `AsyncSession`, and other utilities.
- **E2E tests** -- `test_task` and `test_endpoints` files are end-to-end without mocking. They test actual database interactions and external services where possible.
- **Mocking** -- External services (Stripe, etc.) use `MagicMock` patterns. Avoid redundant fixture setup.

## Usage

Run from `server/`: `uv run task test` (all + coverage), `uv run task test_fast` (parallel), or `uv run pytest tests/path/test_file.py::TestClass::test_method`.

## Learnings

_No learnings recorded yet._
