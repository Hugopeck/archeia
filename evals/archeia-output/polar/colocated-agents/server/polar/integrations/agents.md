## Local Rules

- Each subdirectory wraps one external service. Do not mix multiple external services in one adapter.
- Stripe is the most critical integration; changes require careful webhook handling review.
- External API credentials come from environment variables, never hardcoded.
- Webhook handlers must be idempotent; the same event may be delivered multiple times.
- Test external integrations with mocks (`MagicMock`) or VCR recordings (`pytest-recording`).

## README Maintenance

Before working in this directory, read the README.md.
After completing work, update the README's Learnings section with anything non-obvious you discovered.

Maintains: server/polar/integrations/README.md
