# growth domain (reserved)

No growth skills exist yet. This directory is reserved for future skills that own the `growth/` domain as defined by the [Archeia Standard](../../standard/SCHEMA.md).

## What the standard says

Per `standard/SCHEMA.md`, the `growth/` domain captures how a product acquires, retains, and monetizes users. Growth is its own discipline — it reads from both business (strategy, pricing) and product (features, specs) but is subordinate to neither.

Contents (per the standard):

- `growth/channels/*.md` — acquisition channels: hypothesis, experiments, results, current status
- `growth/metrics/*.md` — KPIs, funnel definitions, benchmarks, cohort analyses

## Current state

Nothing is written to `.archeia/growth/` yet. No skills, no schemas, no canonical writers.

When this domain gets implemented, candidate skills include:

- `channel-experiment` — author a new acquisition-channel hypothesis and experiment log
- `define-metrics` — extract KPI definitions from product/product.md and a growth strategy doc
- `cohort-report` — produce a cohort/funnel analysis from a data source

These are placeholders — no design work has been done. Defer to Phase 3+ or later.

## Reads from

When authored, growth skills will read:

- `business/strategy/*.md` — positioning and pricing context
- `product/product.md` — feature context
