# clarify-idea

Builder-only skill for turning a rough product idea into a saved design brief.

## What it does

- explores a product or tool idea through one-at-a-time builder questions
- checks local prior idea docs for overlap
- optionally runs short privacy-gated web research using generalized terms
- generates 2–3 alternatives and recommends one
- creates one static HTML mockup for UI ideas
- saves a design doc plus light session continuity under `.archeia/business/`

## Saved artifacts

On first use in an adopting repo, the skill should scaffold:

```text
.archeia/
└── business/
    ├── README.md
    ├── ETHOS.md
    ├── drafts/
    └── sessions/
        └── sessions.jsonl
```

Typical outputs:

- `.archeia/business/drafts/...-design.md`
- `.archeia/business/drafts/...-mockup.html` for UI ideas
- `.archeia/business/sessions/...md`
- `.archeia/business/sessions/sessions.jsonl`

## What it does not do

- no implementation or scaffolding of the product itself
- no startup-mode YC questioning
- no telemetry or external state
- no founder-tier relationship system
- no broad competitive strategy work

## Shared references

- `references/ETHOS.md` (alongside this SKILL.md) is the canonical local copy of the upstream ethos.
- The runtime `.archeia/business/ETHOS.md` file is a portable working copy inside the adopting repo.

## Inputs and outputs

The skill expects a rough idea plus enough context to clarify who it is for and what would make it compelling.

The main output is a saved builder brief with a clear recommended approach. For UI ideas, it also saves one lightweight HTML mockup.
