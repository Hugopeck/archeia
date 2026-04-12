# Archeia Output Bundles

Each repo-specific subdirectory under `evals/archeia-output/` contains the
**canonical Phase 3 output bundle** captured from the real Archeia skill
pipeline. Phase 2 may prepare directories or manifests, but bundle contents are
not canonical until the skill pipeline has been run for that repo.

Expected layout:

```
evals/archeia-output/<repo-id>/
  bundle-manifest.json
  AGENTS.md
  CLAUDE.md
  .archeia/
    Architecture.md
    Standards.md
    Guide.md
    System.json
    Containers.json
    Components.json
    DataFlow.json
    diagrams/
  colocated-readmes/
    manifest.json
    ...
  colocated-agents/
    manifest.json
    ...
```

The final bundle must include only canonical generation outputs. Do not ship:

- `.archeia/codebase/scan-report.md`
- `.archeia/codebase/git-report.md`
- temporary caches, virtualenvs, or tool-generated scratch files
- manually authored placeholder docs from pre-Phase-3 experimentation

`bundle-manifest.json` records provenance for the generated bundle, including
source repo, pinned commit, pipeline order, copied files, skipped outputs, and
evidence-validation results.

If `manifest.json` is present for a colocated bundle, it should look like:

```json
[
  {
    "source": "src/api/README.md",
    "target": "src/api/README.md"
  }
]
```

Without a manifest, the harness copies files using their relative paths inside
the colocated bundle directory. Phase 3 requires explicit manifests for both
colocated bundle types.
