---
name: review-draft
description: Review a business draft and produce the locked product.md. Reads a draft under .archeia/business/drafts/, optionally consults .archeia/codebase/architecture/ for feasibility, challenges gaps, then writes the locked product spec at .archeia/product/product.md with Features, Constraints, and Priorities sections. Use when a user has a reviewed draft and wants the spec locked for implementation.
---

# review-draft

Turn a reviewed business draft into the locked `product/product.md` spec. This skill closes the `business → product` contract defined by the Archeia Standard (`standard/SCHEMA.md`).

## When to use

- A draft exists under `.archeia/business/drafts/` with `status: review`.
- The user is ready to convert the draft into an implementation-ready spec.
- Not for initial ideation — use `clarify-idea` or `create-vision` for that.

## Inputs

- `.archeia/business/drafts/<filename>.md` — the draft to review. If multiple candidates exist with `status: review`, ask the user which one.
- `.archeia/business/vision/*.md` — optional context.
- `.archeia/codebase/architecture/architecture.md` + `*.json` — optional feasibility reference. Read if present to validate the draft against actual code.

## Outputs

- `.archeia/product/product.md` — the locked spec (required sections below).
- `.archeia/product/decisions/<YYYYMMDD-HHMMSS>-<slug>.md` — an ADR-style decision record capturing the rationale. Handed off to `lock-spec` for the actual write (optional; you may also write it yourself).

Any existing `product.md` is superseded: rename the old one to `.archeia/product/decisions/superseded-<timestamp>-product.md` before writing the new one.

## Required `product.md` sections

The Archeia Standard requires these three sections so that `execution/` skills can parse the spec and generate tasks:

1. **Features** — each feature has a `name`, `description`, and `acceptance_criteria` (bullet list). Add a stable `id` per feature (slug or ordinal) so tasks can reference it.
2. **Constraints** — technical and business constraints that scope the work. One per line or bulleted list.
3. **Priorities** — ordered list or MoSCoW classification (Must/Should/Could/Won't).

Frontmatter for `product.md`:

```yaml
---
title: string
status: locked
locked_at: ISO 8601 datetime
source_draft: relative path to the business draft that produced this spec
supersedes: optional path to a previous product.md
author: string
---
```

## Workflow

1. **Discover** — list drafts under `.archeia/business/drafts/` with `status: review`. If none, stop and tell the user.
2. **Read** — load the chosen draft. If vision artifacts exist under `.archeia/business/vision/` that reference the same slug, read them too.
3. **Feasibility (optional)** — if `.archeia/codebase/architecture/architecture.md` exists, read it. Cross-reference each feature the draft proposes against the architecture. Flag features that conflict with existing containers/components or that require new infrastructure not in the current system.
4. **Challenge** — for each ambiguous or missing constraint in the draft, either resolve it with the user (AskUserQuestion format) or document it explicitly in the spec as an open question that blocks implementation.
5. **Write** — emit `.archeia/product/product.md` with the required frontmatter and sections. Link back to the source draft in frontmatter.
6. **Record the decision** — write a decision record under `.archeia/product/decisions/` in ADR format:
   - Title
   - Context (why this draft was picked, what alternatives were considered)
   - Decision (what the locked spec commits to)
   - Consequences (what this forecloses, what risks remain)
7. **Update source** — change the draft's `status: review` → `status: locked` and add `locked_into: .archeia/product/product.md` to its frontmatter so the audit trail is traceable. Never delete drafts.

## Non-negotiables

- **Do not invent features that aren't in the draft.** If the draft is incomplete, surface the gap — don't paper over it.
- **Do not silently drop scope.** If you decide to exclude something from the spec, name it explicitly in a `Not in scope` section.
- **Every feature must have acceptance criteria.** A feature without testable criteria is ambiguous — push back.
- **Do not break existing product.md without recording supersession.** Old spec must be archived to `decisions/superseded-*.md`.

## Read by

- Execution skills (`work`, `create`, `decompose`) read `product.md` to generate tasks.
- Future growth skills will read `product.md` for feature context.

## Related skills

- `clarify-idea` — produces drafts this skill reviews.
- `create-vision` — produces vision artifacts this skill may consult.
- `lock-spec` — appends decision records to `.archeia/product/decisions/` (may be called separately, or rolled into this skill's workflow).
