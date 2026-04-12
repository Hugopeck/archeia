---
name: lock-spec
description: Append an ADR-style decision record to .archeia/product/decisions/ capturing why a product.md was locked or updated. Use when you need to record the rationale behind a product spec decision without running a full review pass. Typically invoked by review-draft or directly by a human owner finalizing a spec.
---

# lock-spec

Write a single ADR-style decision record under `.archeia/product/decisions/`. Per the Archeia Standard, the `product/decisions/` directory is append-only — decisions are never modified, only superseded by a newer decision that explicitly references the predecessor.

## When to use

- `review-draft` finished producing a locked `product.md` and you want the rationale captured separately.
- A human is manually editing `product.md` and wants to record why.
- An earlier decision needs to be superseded with a new one (the new decision explicitly names the old).

## Inputs

- The current `.archeia/product/product.md` (must exist).
- A short rationale from the user or the calling skill (context, alternatives considered, decision, consequences).
- Optionally, a `supersedes:` filename pointing at a prior decision record.

## Output

A new file at `.archeia/product/decisions/<YYYYMMDD-HHMMSS>-<slug>.md` with:

```yaml
---
title: string
status: accepted | superseded
created: ISO 8601 datetime
supersedes: optional relative path to prior decision
related_spec: .archeia/product/product.md
author: string
---
```

And the body follows the ADR format:

```markdown
# <Title>

## Context
<What prompted this decision. Link to the draft, vision artifact, or event that triggered it.>

## Decision
<What was decided. Be concrete — name specific features, constraints, or scope boundaries.>

## Consequences
<What this decision enables, forecloses, and risks. Name the tradeoffs explicitly.>

## Alternatives considered
<2-3 alternatives and why each was rejected.>
```

## Non-negotiables

- **Append-only.** Never edit or delete an existing decision record. To overturn a prior decision, write a new one with `supersedes:` pointing at it.
- **Decisions cite their source.** Every decision must link to the `product.md` it pertains to and, when applicable, the draft or vision artifact it derives from.
- **No retroactive edits.** If the current spec differs from what a decision records, either (a) write a new decision that supersedes the old, or (b) fix the spec. Never silently reshape history.

## Workflow

1. Confirm `.archeia/product/product.md` exists. If not, stop and tell the user — decisions must attach to a real spec.
2. Ask the user (or accept from the caller) for: title, context, decision, consequences, alternatives.
3. If this supersedes a prior decision, find the prior file and verify it exists. Update its frontmatter `status:` to `superseded` in a single, minimal edit (this is the only permitted mutation of an existing decision).
4. Write the new file at `.archeia/product/decisions/<timestamp>-<slug>.md`.
5. Print the created path and a one-line summary.

## Read by

- Humans and agents reviewing the history of `product.md`.
- Future `review-draft` runs that want to know whether a proposed change conflicts with a prior accepted decision.
