# Cron Runner Components

```mermaid
flowchart LR
    postgresql[("PostgreSQL<br/><i>PostgreSQL</i>")]

    subgraph cron-runner["Cron Runner"]
        cron-jobs["Cron Jobs<br/><i>TypeScript</i>"]
    end

    cron-jobs -->|"Reads and updates data for scheduled maintenance tasks"| postgresql
```

**Source:** `.archeia/codebase/architecture/components.json`
**Generated:** 2026-04-10
