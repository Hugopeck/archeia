# Scan Report

> Python / pytest / uv | 72.3k LOC | 3 modules | ~706.1k tokens

## Size

| Language | Files | Lines |
|----------|-------|-------|
| Python | 92 | 38,738 |
| Markdown | 97 | 15,116 |
| JSON | 11 | 11,053 |
| HTML | 7 | 5,079 |
| Lockfile | 1 | 1,791 |
| Other | 12 | 562 |
| **Total** | **220** | **72,339** |

## Token Estimates

| Directory | Est. Tokens | % of Total |
|-----------|-------------|------------|
| docs | 183,778 | 26.0% |
| tests | 180,534 | 25.6% |
| engine | 115,518 | 16.4% |
| (root) | 93,527 | 13.2% |
| scripts | 68,043 | 9.6% |
| tasks | 44,683 | 6.3% |
| reports | 8,181 | 1.2% |
| collector | 7,007 | 1.0% |
| .gstack | 2,210 | 0.3% |
| .github | 1,354 | 0.2% |
| deploy | 1,252 | 0.2% |

## Structure

```text
repo-root/ (228 files)
├── tasks/ (62 files)
│   ├── triage/ (47 files)
│   ├── projects/ (9 files)
│   └── findings/ (5 files)
├── tests/ (45 files)
│   ├── engine/ (28 files)
│   ├── collector/ (6 files)
│   ├── scripts/ (6 files)
│   └── fixtures/ (3 files)
├── docs/ (33 files)
│   ├── runbooks/ (7 files)
│   ├── technical_plan/ (5 files)
│   ├── ADR/ (4 files)
│   ├── archive/ (3 files)
│   ├── incidents/ (3 files)
│   ├── vendor/ (3 files)
│   ├── hedging_strategy/ (2 files)
│   ├── cso/ (1 files)
│   ├── releases/ (1 files)
│   └── retros/ (1 files)
├── engine/ (26 files)
│   ├── ui/ (8 files)
│   ├── futuur/ (5 files)
│   ├── compute/ (3 files)
│   └── polymarket/ (3 files)
├── scripts/ (23 files)
├── collector/ (8 files)
├── deploy/ (6 files)
├── .github/ (4 files)
│   └── workflows/ (4 files)
├── .gstack/ (1 files)
│   └── security-reports/ (1 files)
├── data/ (1 files)
│   └── reports/ (1 files)
└── reports/ (1 files)
```

## Modules

| Module | Source Files |
|--------|--------------|
| scripts | 23 |
| engine | 22 |
| collector | 8 |

## README Coverage

| Directory | Source Files | Has README |
|-----------|--------------|------------|
| ./ | 96 | Yes |
| tests/ | 42 | No |
| tests/engine/ | 28 | No |
| scripts/ | 23 | No |
| engine/ | 22 | No |
| collector/ | 8 | No |
| tests/engine/futuur/ | 8 | No |
| tests/collector/ | 6 | No |
| tests/scripts/ | 6 | No |
| engine/futuur/ | 5 | No |

**9 of 10 directories need READMEs**

## Dependencies

| Manifest | Direct Deps | Dev Deps |
|----------|-------------|----------|
| pyproject.toml | 6 | 8 |

## Test Footprint

- Test files: 45
- Source files: 51
- Test-to-source ratio: 0.88
- Frameworks: pytest

## Git Vitals

- Repo age: 2026-02-23 (first commit)
- Total commits: 120
- Contributors: 3
- Last commit: 2026-04-02
- Remote branches: 35

## Signals

- CI workflows: 4
- Docker: Dockerfile present (deploy/Dockerfile, deploy/engine.Dockerfile), no compose file
- TODO/FIXME: 32 total (tasks 16, (root) 11, docs 5)
- Entry points: 1 (index.html)
- Large files (>1MB): 0 (none)
