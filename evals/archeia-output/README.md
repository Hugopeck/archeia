# Archeia Output Bundles

Each repo-specific subdirectory under `evals/archeia-output/` contains the
**canonical Phase 3 output bundle** captured from the real Archeia skill
pipeline. Phase 2 may prepare directories or manifests, but bundle contents are
not canonical until the skill pipeline has been run for that repo.

> **Note on layout migration (Phase 1 of the archeia monorepo):** The bundles
> under each `<repo-id>/.archeia/` were originally captured with a flat
> layout (`.archeia/Architecture.md`, `.archeia/System.json`, etc.). When
> the former `archeia`, `hstack`, and `track` projects were merged into
> this monorepo under the Archeia Standard, every bundle was restructured
> in-place into the standard-compliant `.archeia/codebase/` subtree. The
> file *content* is unchanged from the original Phase 3/4 runs — only
> the paths were rewritten. History for each move is preserved via
> `git mv`, so `git log --follow` on any file walks back through the
> original flat-path commit. `bundle-manifest.json` files in each repo
> subdir were updated to reference the new paths.

Expected layout:

```
evals/archeia-output/<repo-id>/
  bundle-manifest.json
  AGENTS.md
  CLAUDE.md
  .archeia/
    codebase/
      architecture/
        architecture.md
        system.json
        containers.json
        components.json
        dataflow.json
        entities.json        # when ORM/schema detected
        statemachine.json    # when state machines detected
      standards/
        standards.md
      guide.md
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
