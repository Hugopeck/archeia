# archeia:write-readmes

A skill that generates colocated READMEs across a repository so every significant directory has human-readable context next to its code.

## What it does

Reads `.archeia/codebase/scan-report.md` (from `archeia:scan-repo`) to find directories that need READMEs, then creates or updates a `README.md` in each one.

Each generated README includes:
- **Title and Purpose** — what the directory does and its role in the system
- **Structure** — mermaid diagram or annotated tree of internal organization
- **Key Concepts** — the 3–5 things to know before working here
- **Usage** — how other parts of the codebase consume this module

## What it doesn't do

- Generate a root README (too personal/project-specific)
- Duplicate content from Guide.md, Standards.md, or AGENTS.md
- Delete human-written content when updating existing READMEs

## Prerequisites

Run `archeia:scan-repo` first. This skill reads its README Coverage output to determine which directories to process.

## Philosophy

See `references/README_PROTOCOL.md` for the full protocol — why colocated READMEs, what goes in, what stays out, and how they work alongside CLAUDE.md and AGENTS.md in the agentic era.
