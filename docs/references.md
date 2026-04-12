# References

Resources that inform the design and methodology behind Archeia skills.

## Architecture and Documentation Frameworks

- [C4 Model](https://c4model.com/) — System, Container, Component diagram methodology used in JSON templates
- [arc42](https://arc42.org/overview) — 12-section architecture documentation template
- [Diátaxis](https://docs.diataxis.fr/) — Framework for categorizing docs into tutorials, guides, reference, explanation
- [Architecture Decision Records](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — Michael Nygard's original ADR proposal
- [Structurizr DSL](https://github.com/structurizr/dsl) — C4 models expressed as code

## Agent-Readable Documentation

- [agents.md](https://www.agents.md/) — Proposed standard for agent-readable documentation in repos
- [CLAUDE.md](https://docs.anthropic.com/en/docs/claude-code/memory) — Anthropic's docs on Claude Code memory files and project context

## Development Standards

- [Google Style Guides](https://google.github.io/styleguide/) — Gold standard collection of style guides for C++, Java, Python, Shell, TypeScript, and more
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) — Most widely adopted community JavaScript/React style guide
- [Microsoft API Guidelines](https://github.com/microsoft/api-guidelines) — Authoritative reference for designing RESTful API standards
- [thoughtbot Guides](https://github.com/thoughtbot/guides) — Comprehensive guides covering code style, code review, and project conventions
- [GitLab Handbook](https://handbook.gitlab.com/) — Most transparent and complete public engineering handbook, covering standards governance
- [Spotify Engineering Culture](https://engineering.atspotify.com/2014/03/spotify-engineering-culture-part-1/) — Influential model for how teams organize standards, autonomy, and alignment

## Runbooks, Guides, and Operational Handbooks

- [Google SRE Book](https://sre.google/sre-book/table-of-contents/) — Definitive reference on operational practices, runbooks, incident response, and on-call procedures
- [PagerDuty Incident Response](https://response.pagerduty.com/) — Open-source incident response guide covering on-call, severity levels, and post-mortems
- [PagerDuty IR Docs (source)](https://github.com/pagerduty/incident-response-docs) — Forkable template for building your own runbooks
- [Basecamp Handbook](https://github.com/basecamp/handbook) — Publicly available company handbook on GitHub, great onboarding template
- [Write the Docs](https://www.writethedocs.org/guide/) — Community guide for developer documentation best practices

## Technical Writing and Docs-as-Code

- [Docs as Code](https://www.docops.io/docs-as-code/) — Treating documentation with the same rigor as source code
- [Google Technical Writing](https://developers.google.com/tech-writing) — Free courses on clarity, conciseness, and structured documentation
- [GitHub Docs Style Guide](https://docs.github.com/en/contributing/style-guide-and-content-model/style-guide) — Voice, tone, formatting conventions, and terminology standards
- [GitHub Docs Article Structure](https://docs.github.com/en/contributing/style-guide-and-content-model/contents-of-a-github-docs-article) — Required structure and sections for every documentation article
- [Open Source Guides](https://opensource.guide/) — GitHub's guides on READMEs, contributing docs, and documentation best practices

## Documentation Tooling

- [Markdoc](https://markdoc.dev/) — Stripe's open-source doc authoring framework, purpose-built for technical docs at scale
- [Docusaurus](https://docusaurus.io/) — Meta's open-source documentation site generator with versioning, search, and Markdown extensions
- [Stripe API Reference](https://docs.stripe.com/api) — Industry benchmark for API documentation structure
- [Stripe OpenAPI Spec](https://github.com/stripe/openapi) — Machine-readable API docs maintained alongside human-readable docs
- [Next.js Docs](https://nextjs.org/docs) — Widely praised for progressive disclosure and clear API references
- [Next.js Docs Contributing Guide](https://github.com/vercel/next.js/tree/canary/contributing/docs) — Vercel's internal standards for documentation quality
- [github/docs](https://github.com/github/docs) — Full documentation-as-code system at enterprise scale

## Git History Analysis & Team Metrics

### Methodology

- [Adam Tornhill — "Your Code as a Crime Scene"](https://pragprog.com/titles/atcrime2/your-code-as-a-crime-scene-second-edition/) — Hotspot analysis, bus factor from git history, change coupling
- [DORA Metrics](https://dora.dev/guides/dora-metrics-four-keys/) — Deployment frequency, lead time, change failure rate, MTTR
- [SPACE Framework](https://queue.acm.org/detail.cfm?id=3454124) — Developer productivity dimensions: Satisfaction, Performance, Activity, Communication, Efficiency (ACM)
- [git-log format placeholders](https://git-scm.com/docs/pretty-formats) — `%aN`, `%aI`, `%s`, `%b` and other format specifiers used for data extraction
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) — Commit message specification for structured prefixes (feat, fix, chore, etc.)

### Existing Tools (for deeper analysis beyond archeia-scan-git)

- [git-quick-stats](https://github.com/git-quick-stats/git-quick-stats) — Commit statistics by time, author, and timezone
- [git-fame](https://github.com/casperdcl/git-fame) — Blame-based line ownership per author
- [git-of-theseus](https://github.com/erikbern/git-of-theseus) — Code age and survival curves
- [hercules](https://github.com/src-d/hercules) — ML-ready burndown analysis
- [git-sizer](https://github.com/github/git-sizer) — Repository health and object metrics
- [gitinspector](https://github.com/ejwa/gitinspector) — Per-file responsibility matrices
- [CNCF Velocity](https://github.com/cncf/velocity) — Cross-project velocity tracking via BigQuery
- [bus-factor-explorer](https://github.com/JetBrains-Research/bus-factor-explorer) — Interactive bus factor analysis with treemap visualization
- [SOM-Research/busfactor](https://github.com/SOM-Research/busfactor) — Directory-level bus factor calculation
- [cocogitto](https://github.com/cocogitto/cocogitto) — Conventional commits toolbox (linting, changelog, versioning)
- [RepoSense](https://github.com/reposense/RepoSense) — Contribution analysis and visualization for groups of repositories

## Mermaid Diagrams

- [Mermaid.js](https://mermaid.js.org/) — Official docs covering all diagram types with full syntax references
- [Mermaid Live Editor](https://mermaid.live/) — Browser-based editor for writing and previewing Mermaid diagrams in real time
- [Mermaid GitHub](https://github.com/mermaid-js/mermaid) — Source repo with examples and integration documentation
- [GitHub Mermaid Support](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams) — Official guide on using Mermaid diagrams natively in GitHub Markdown
