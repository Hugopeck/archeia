# create-vision

Solo-builder skill for turning an idea doc or rough feature plan into a saved vision before implementation.

## What it does

- takes a saved idea from `clarify-idea` or a rough plan file as input
- challenges premises, compares 2–3 approaches, and clarifies scope
- uses a mode-based review process (scope expansion / selective / hold / reduction) adapted for solo builders
- keeps scope changes explicit and one decision at a time
- saves a vision artifact plus light session continuity under `.archeia/business/`

## Saved artifacts

On first use in an adopting repo, the skill should scaffold:

```text
.archeia/
└── business/
    ├── README.md
    ├── ETHOS.md
    ├── drafts/
    ├── vision/
    └── sessions/
        └── sessions.jsonl
```

Typical outputs:

- `.archeia/business/vision/...-vision.md`
- `.archeia/business/sessions/...-create-vision.md`
- `.archeia/business/sessions/sessions.jsonl`

## How it differs from `clarify-idea`

- `clarify-idea` explores a rough concept and saves an idea doc
- `create-vision` takes that idea doc, or a rough plan, and turns it into a sharper vision artifact before implementation
- `clarify-idea` is about discovering the thing
- `create-vision` is about choosing the right version of the thing

## What it does not do

- no implementation or scaffolding
- no VC or startup-founder coaching
- no global state, telemetry, or external binaries
- no full engineering review pipeline

## Shared references

- `references/ETHOS.md` (alongside this SKILL.md) is the canonical local copy of the builder ethos.
- The runtime `.archeia/business/ETHOS.md` file is a portable working copy inside the adopting repo.

## Audience

This skill is for solo builders and indie hackers.

It assumes bootstrapping by default and tries to make the ambitious version fit one person plus AI, not a venture-backed org chart.
