# integrations

Third-party service adapters connecting Polar to external platforms. Each subdirectory wraps an external API with Polar-specific logic for authentication, data synchronization, and event handling.

## Structure

```mermaid
graph LR
    STRIPE[stripe/] -->|payments, subs| API[API Server]
    GITHUB[github/] -->|OAuth, repos| API
    DISCORD[discord/] -->|server access| BENEFIT[benefit/]
    APPLE[apple/] -->|sign-in| AUTH[auth/]
    GOOGLE[google/] -->|sign-in| AUTH
    LOOPS[loops/] -->|email marketing| WORKER
    PLAIN[plain/] -->|support tickets| WORKER
    TINYBIRD[tinybird/] -->|analytics| EVENTS
    AWS[aws/] -->|S3 storage| FILES
```

## Key Concepts

- **Stripe** -- Payment processing, subscription management, Connect payouts, webhook handling. Central to all financial operations.
- **GitHub** -- OAuth authentication, repository benefit grants (adding collaborators), GitHub App webhooks.
- **Discord** -- Server role grants as a product benefit via Discord bot integration.
- **Tinybird** -- Real-time analytics and event ingestion for usage-based billing meters.
- **Loops, Plain** -- Email marketing automation and customer support integrations.

## Usage

Integration modules are consumed by domain modules (`checkout/`, `benefit/`, `auth/`, `payout/`) and by background workers for webhook processing and async operations.

## Learnings

_No learnings recorded yet._
