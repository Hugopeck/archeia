# business domain (reserved)

No dedicated business skills exist yet. This directory is reserved for future skills that own the `business/` domain as defined by the [Archeia Standard](../../standard/SCHEMA.md).

## What the standard says

Per `standard/SCHEMA.md`, the `business/` domain captures the holistic business vision — why this product exists, who it's for, how it makes money, and what the competitive landscape looks like. It's the upstream input to everything else.

Contents (per the standard):

- `business/vision/*.md` — vision artifacts, design briefs
- `business/landscape/*.md` — market research, competitors, whitespace
- `business/strategy/*.md` — business model, positioning, pricing, GTM
- `business/drafts/*.md` — product-vision drafts, pre-review, pre-lock

## Current state

The `.archeia/business/` output tree is **already partially populated** by the product-domain skills ported from hstack:

- `archeia:clarify-idea` writes `.archeia/business/drafts/*.md`
- `archeia:create-vision` writes `.archeia/business/vision/*.md`

This is a deliberate interim arrangement: hstack historically owned these workflows, and rather than force-split its skills across two domains, Phase 2 keeps them under `skills/product/` while their outputs land in `.archeia/business/`. The standard's ownership model (SCHEMA.md §Ownership Model) would formally require dedicated business skills to own these writes.

A future Phase 3+ task can either:

1. Move `clarify-idea` and `create-vision` from `skills/product/` into `skills/business/` to align ownership with the standard, or
2. Author new, dedicated `business/` skills (e.g. `research-landscape`, `define-strategy`) that complement the existing product-domain skills.

Until then, treat `.archeia/business/` as product-domain territory in practice.

## Not in this domain yet

- Market research / competitor analysis skills
- Pricing / positioning / GTM strategy skills
- Landscape analysis skills
