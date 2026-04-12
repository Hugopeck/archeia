# Gold-Standard Output Examples

These examples show what generated `.archeia/` documents should look like for
a real project. The quality bar here is what separates useful architecture docs
from generic filler: specific, evidence-grounded claims that tell you something
you couldn't learn from running `ls`.

Study them before generating. Pay attention to how each example uses domain
language, cites real file paths, and makes every sentence earn its place.

---

## Example 1: Architecture.md for a Django prediction market

This is the most important example — Architecture.md is the document that
anchors everything else. Notice how it builds progressively: what the system
*is* (Overview), how it's *shaped* (Topology), how the pieces *connect*
(Boundaries), how data *moves* (Flow), what gets *stored* (Model), and how
objects *change over time* (Lifecycles).

```markdown
## System Overview

This is a Python 3.11 API built with Django 4.2 and Django REST Framework.
It operates a prediction market platform where users create markets, place
wagers, and settle positions when markets resolve.

**Evidence:** `pyproject.toml` (django==4.2.7, djangorestframework==3.14.0),
`manage.py`

## Topology

- **Type:** Modular monolith
- **Primary areas:** `wager/` (market and wagering engine), `account/`
  (identity and auth), `finance/` (double-entry ledger), `importer/`
  (external market data sync), `notification/` (email and push),
  `api/` (versioned REST endpoints)
- **External systems:** PostgreSQL 15 (via `psycopg2-binary` in
  `pyproject.toml`), Redis 7 (via `django-redis` in `pyproject.toml`),
  Stripe (via `stripe` in `pyproject.toml`), Celery (via `celery` in
  `pyproject.toml`)

**Evidence:** `pyproject.toml`, `docker-compose.yml`, `manage.py`

## Module Boundaries

| Module | Path | Responsibility | Dependencies |
|--------|------|---------------|-------------|
| Wager | `wager/` | Market creation, order matching, position management, settlement | `finance/`, `notification/` |
| Account | `account/` | User identity, OAuth2, KYC, financial accounts | `finance/` |
| Finance | `finance/` | Double-entry ledger, deposits, withdrawals | (none — leaf module) |
| Importer | `importer/` | External market data sync from third-party APIs | `wager/` |
| Notification | `notification/` | Email, push notifications, webhook delivery | `account/`, `wager/` |
| API | `api/` | Versioned REST endpoints (v1, v1.5, v2.0) | all modules |

**Evidence:** directory listing, import patterns in `api/v2_0/views.py`,
`wager/tasks.py`, `notification/tasks.py`

## Data Flow

| Step | Source | Target | Message | Type | Protocol | Evidence |
|------|--------|--------|---------|------|----------|----------|
| 1 | End User | API Server | POST /api/v2/wagers/ | sync | HTTPS | `api/v2_0/views.py` |
| 2 | API Server | Wager Service | create_wager(user, question, outcome, amount) | sync | function call | `api/v2_0/views.py` |
| 3 | Wager Service | Order Book | match_orders(limit_order) | sync | function call | `wager/contrib.py` |
| 4 | Order Book | PostgreSQL | INSERT wager, UPDATE positions | sync | SQL | `wager/models/order_book.py` |
| 5 | Wager Service | Finance Ledger | create_ledger_entry(debit, credit) | sync | function call | `wager/tasks.py` |
| 6 | API Server | End User | 201 Created {wager_id, shares, price} | response | HTTPS | `api/v2_0/serializers.py` |
| 7 | API Server | Celery Worker | enqueue notification task | async | Redis/Celery | `notification/tasks.py` |

**Evidence:** import chains in `api/v2_0/views.py` → `wager/contrib.py` →
`wager/models/order_book.py` → `finance/models.py`

## Data Model

- **ORM/Schema technology:** Django ORM (django==4.2.7)

| Entity | Source File | Description | Key Fields |
|--------|------------|-------------|------------|
| Question | `wager/models/question.py` | A prediction market with outcomes | title (str), status (enum), bounded_loss (decimal), scoring_rule (enum) |
| Outcome | `wager/models/outcome.py` | One possible result of a market | name (str), question_fk, current_price (decimal) |
| Wager | `wager/models/wager.py` | User's net position on one outcome | user_fk, outcome_fk, shares (decimal), status (enum) |
| LimitOrder | `wager/models/limit_order.py` | Buy/sell order in the order book | user_fk, outcome_fk, price (decimal), type (enum) |
| User | `account/models/user.py` | Platform user with auth and KYC | email (str), kyc_status (enum), privy_id (str) |

- `Question` 1→N `Outcome` (has) — `wager/models/outcome.py`
- `Question` 1→N `LimitOrder` (receives) — `wager/models/limit_order.py`
- `Outcome` 1→N `Wager` (produces) — `wager/models/wager.py`
- `User` 1→N `Wager` (places) — `wager/models/wager.py`
- `User` 1→N `LimitOrder` (submits) — `wager/models/limit_order.py`

**Evidence:** `wager/models/question.py`, `wager/models/wager.py`,
`account/models/user.py`

## State Lifecycles

**Question lifecycle** (`wager/models/question.py`):
States: draft → open → closed → resolved
Transitions:
- draft → open: publish (admin action) — `wager/admin.py`
- open → closed: close_market (scheduled task) — `wager/tasks.py`
- closed → resolved: resolve (admin selects winning outcome) — `wager/admin.py`
- draft → cancelled: cancel — `wager/admin.py`
- open → cancelled: cancel — `wager/admin.py`

**Wager lifecycle** (`wager/models/wager.py`):
States: purchased → sold | win | lost | cancelled | disabled
Transitions:
- purchased → sold: user sells position — `wager/contrib.py`
- purchased → win: market resolves in favor — `wager/tasks.py`
- purchased → lost: market resolves against — `wager/tasks.py`
- purchased → cancelled: market cancelled — `wager/tasks.py`

**Evidence:** `wager/models/question.py` (QuestionStatus enum),
`wager/models/wager.py` (WagerStatus enum), `wager/tasks.py` (settlement logic)
```

**Why this works:**
- Every claim cites a file path — you can verify any statement by reading the
  cited file
- Module Boundaries shows actual import dependencies, not guessed ones
- Data Flow uses the structured table with sync/async/response types —
  you can see at a glance that steps 1-5 are the synchronous request/response
  cycle and step 7 is fire-and-forget
- Data Model lists real fields from real model files, not "this module
  probably has a User model"
- State Lifecycles trace each transition to the code that implements it —
  an admin action in `admin.py` vs a scheduled task in `tasks.py`
- Domain language throughout: "prediction market," "order matching,"
  "settlement" — not "Django app with models and views"

---

## Example 2: System.json for the same project

System.json is the C4 Level 1 view — the highest zoom level. It models the
system as a single box surrounded by the people who use it and the external
systems it depends on. The key thing to notice here is how each entity uses
domain-specific names ("Market Participant," not "End User") and how every
relationship describes *what happens*, not just that a connection exists.

```json
{
  "level": 1,
  "title": "System Context",
  "system": {
    "id": "futuur-api",
    "name": "Futuur Prediction Market API",
    "description": "REST backend for prediction market wagering, settlement, and user management",
    "technology": "Python 3.11 / Django 4.2",
    "evidence": ["pyproject.toml", "manage.py"]
  },
  "people": [
    {
      "id": "end-user",
      "name": "Market Participant",
      "description": "Places wagers on prediction market outcomes",
      "evidence": ["api/v2_0/views.py"]
    },
    {
      "id": "admin",
      "name": "Market Administrator",
      "description": "Creates markets, resolves outcomes, manages users",
      "evidence": ["wager/admin.py", "account/admin.py"]
    }
  ],
  "external_systems": [
    {
      "id": "postgresql",
      "name": "PostgreSQL",
      "description": "Primary relational data store for markets, wagers, and users",
      "technology": "PostgreSQL 15",
      "evidence": ["docker-compose.yml", "pyproject.toml"]
    },
    {
      "id": "redis",
      "name": "Redis",
      "description": "Celery broker, session cache, and rate limiting",
      "technology": "Redis 7",
      "evidence": ["docker-compose.yml", "pyproject.toml"]
    },
    {
      "id": "stripe-api",
      "name": "Stripe API",
      "description": "Payment processing for deposits and withdrawals",
      "technology": "HTTPS",
      "evidence": ["pyproject.toml"]
    }
  ],
  "relationships": [
    {
      "source": "end-user",
      "target": "futuur-api",
      "description": "Places wagers and manages positions via REST API",
      "technology": "HTTPS/JSON",
      "evidence": ["api/v2_0/views.py"]
    },
    {
      "source": "admin",
      "target": "futuur-api",
      "description": "Manages markets and users via Django admin",
      "technology": "HTTPS",
      "evidence": ["wager/admin.py"]
    },
    {
      "source": "futuur-api",
      "target": "postgresql",
      "description": "Reads and writes market, wager, and user records",
      "technology": "SQL",
      "evidence": ["wager/models/question.py"]
    },
    {
      "source": "futuur-api",
      "target": "redis",
      "description": "Enqueues async tasks and caches sessions",
      "technology": "Redis protocol",
      "evidence": ["notification/tasks.py"]
    },
    {
      "source": "futuur-api",
      "target": "stripe-api",
      "description": "Processes deposits and withdrawal requests",
      "technology": "HTTPS/JSON",
      "evidence": ["finance/contrib.py"]
    }
  ]
}
```

**What to notice:**
- IDs are kebab-case and deterministic (`futuur-api`, not `system-1`)
- People use domain names ("Market Participant") — a small thing that makes
  the diagram immediately readable in a meeting
- Descriptions are one sentence, no marketing language
- Every entity has an evidence array with at least one real file path
- Relationships connect every entity — no orphans floating disconnected
- External systems match what's actually in docker-compose.yml and pyproject.toml,
  not what someone remembered from a whiteboard session

---

## Example 3: DataFlow.json showing sync, async, and response types

Like the C4 JSON examples earlier in this file, this is a positive-case
example. Use the `Containers.json`, `Components.json`, and `DataFlow.json`
shapes only when the corresponding structures can be traced with evidence;
otherwise the skill must emit an explicit insufficiency outcome instead of
fabricating the file.

DataFlow.json is the structured version of Architecture.md's Data Flow table.
It captures the same interactions but in machine-readable form — this is what
sequence diagrams render from. This is the positive case: use this shape only
when a primary interaction flow can be traced with evidence. If no such flow
can be evidenced, the skill must emit an explicit insufficiency outcome
instead of fabricating `DataFlow.json`. The important thing here is the three
step types: `sync` for blocking calls, `response` for the return path, and
`async` for fire-and-forget. Together they model both the request cycle and
the background work that happens after the response is sent.

```json
{
  "level": 3,
  "title": "Data Flow",
  "depends_on": "Containers.json",
  "flows": [
    {
      "id": "place-wager",
      "name": "Place Wager",
      "description": "User places a bet on a prediction market outcome",
      "primary": true,
      "participants": [
        { "id": "end-user", "name": "Market Participant", "type": "person" },
        { "id": "futuur-api", "name": "API Server", "type": "container" },
        { "id": "wager-engine", "name": "Wager Engine", "type": "component" },
        { "id": "postgresql", "name": "PostgreSQL", "type": "external_system" },
        { "id": "celery-worker", "name": "Celery Worker", "type": "container" }
      ],
      "steps": [
        {
          "order": 1,
          "source": "end-user",
          "target": "futuur-api",
          "message": "POST /api/v2/wagers/ {outcome_id, amount}",
          "type": "sync",
          "protocol": "HTTPS",
          "evidence": ["api/v2_0/views.py"]
        },
        {
          "order": 2,
          "source": "futuur-api",
          "target": "wager-engine",
          "message": "create_wager(user, outcome, amount)",
          "type": "sync",
          "protocol": "function call",
          "evidence": ["wager/contrib.py"]
        },
        {
          "order": 3,
          "source": "wager-engine",
          "target": "postgresql",
          "message": "INSERT wager + UPDATE order_book",
          "type": "sync",
          "protocol": "SQL",
          "evidence": ["wager/models/order_book.py"]
        },
        {
          "order": 4,
          "source": "wager-engine",
          "target": "futuur-api",
          "message": "{wager_id, shares, price}",
          "type": "response",
          "protocol": "function call",
          "evidence": ["wager/contrib.py"]
        },
        {
          "order": 5,
          "source": "futuur-api",
          "target": "end-user",
          "message": "201 Created",
          "type": "response",
          "protocol": "HTTPS",
          "evidence": ["api/v2_0/views.py"]
        },
        {
          "order": 6,
          "source": "futuur-api",
          "target": "celery-worker",
          "message": "send_wager_confirmation.delay(wager_id)",
          "type": "async",
          "protocol": "Redis/Celery",
          "evidence": ["notification/tasks.py"]
        }
      ],
      "evidence": ["api/v2_0/views.py", "wager/contrib.py", "notification/tasks.py"]
    }
  ]
}
```

**What to notice:**
- All three step types in action: `sync` (steps 1-3 — the request goes
  deeper), `response` (steps 4-5 — the answer comes back up), `async`
  (step 6 — work that happens after the user gets their response)
- Participant IDs resolve to entities in System.json and Containers.json —
  the data model stays consistent across all `.archeia/` files
- Messages use domain language: "create_wager," not "processRequest"
- The async step shows the actual Celery call signature with `.delay()` —
  specific enough that someone reading this can find the exact code
- Response steps explicitly model the return path, not just the request arrows

---

## Anti-Pattern: The Generic Architecture.md

This is what the template is designed to prevent. Compare it to Example 1 above
and notice how every line could apply to literally any web application.

```markdown
## System Overview

This is a modern web application built with industry-standard technologies.
It follows best practices for scalable, maintainable software development.

## Module Boundaries

| Module | Path | Responsibility |
|--------|------|---------------|
| Backend | `src/` | Server-side logic |
| Frontend | `app/` | Client-side UI |
| Tests | `tests/` | Test suite |
| Config | `config/` | Configuration files |

## Data Flow

1. User sends request
2. Server processes request
3. Database stores data
4. Response returned
```

**Why this fails:**
- "Modern web application" and "industry-standard" are marketing, not evidence
  — what language? what framework? what version?
- No file paths cited anywhere — impossible to verify any claim
- Module table is just the directory listing with generic labels — you learn
  nothing beyond what `ls` would tell you
- Data Flow could describe literally any web application ever built — there's
  no mention of what *this* system actually does with data
- Nothing domain-specific: is this an e-commerce platform? A prediction market?
  A healthcare system? Impossible to tell
- A developer reading this learns nothing. An agent reading this invents
  everything.
