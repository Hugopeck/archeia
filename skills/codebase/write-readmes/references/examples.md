# Gold-Standard README Examples

These are real examples of the quality bar this skill must hit. Study them
before generating. Each one was written from deep source code reading — not
from directory listings or framework assumptions.

---

## Example 1: Top-level module (wager/)

```markdown
# wager

Implements prediction market wagering — position creation, order book matching,
and P&L settlement for binary and multi-outcome markets. When a user places a
bet on Futuur, the lifecycle from order to payout runs through here.

## Structure

\`\`\`mermaid
graph LR
    API[api/ versions] -->|user places bet| S[contrib.py]
    S -->|price calculation| LSLMSR[contrib.ls_lmsr]
    LO[models/limit_order.py] -->|match orders| OB[models/order_book.py]
    OB -->|create matches| MO[models/match_order.py]
    MO -->|update positions| W[models/wager.py]
    W -->|settle P&L| T[tasks.py]
    T -->|update balances| Fin[finance/]
    Q[models/question.py] -->|resolve market| W
\`\`\`

## Key Concepts

- **Question = Market** — `Question` is the central market entity with outcomes,
  scoring rules (basic, LMSR, LS-LMSR), and lifecycle states (draft → open →
  closed → resolved). Supports binary (2 outcomes) and multi-outcome markets.
- **Order book with mirrored orders** — `OrderBook` builds normalized bid/ask
  views. For binary markets, it mirrors orders across outcomes via `1 - price`.
  `LimitOrder` supports limit, market, and mirror order types with maker/taker
  fee structures.
- **Wager as consolidated position** — A `Wager` represents a user's net
  position on one outcome in one currency. States: purchased → sold/win/lost/
  cancelled/disabled. All currency amounts use `djmoney.Money` objects via
  `ExtendedMoneyField`.
- **LS-LMSR pricing** — `contrib.py` delegates to `contrib.ls_lmsr.LsLmsr` for
  price calculations with bounded loss and tax parameters per currency mode
  (play money vs real money).
- **Dual currency modes** — Every market operates in both play money (`OOM`)
  and real money (canonical currency), filtered via `CurrencyModeQuerySet`.

## Usage

The API layer (`api/v1/`, `api/v1_5/`, `api/v2_0/`) imports `wager.models` for
serialization and `wager.contrib` for price calculations. `importer/` syncs
external market data into `Question`/`Outcome` structures. `notification/` is
called on resolution for win/loss emails and push notifications. `doubleentry/`
handles the accounting entries for every wager transaction. `market_maker/`
places automated orders through the order book.
```

**Why this works:**
- Title tells you the domain (prediction markets) and the operations (wagering,
  matching, settlement) — not "Contains the wager package"
- Mermaid shows the actual data flow from API → pricing → order book → matching
  → settlement → finance, with domain-specific edge labels
- Key Concepts are unique to this module: LS-LMSR pricing, mirrored order books,
  dual currency modes — you won't find these in any other module's README
- Usage explains what each consumer does: API serializes, importer syncs,
  notification alerts, doubleentry creates ledger entries

---

## Example 2: Nested model layer (wager/models/)

```markdown
# wager/models

Core domain models for the Futuur prediction market — markets (questions),
outcomes, pricing, order books, limit orders, wager positions, and settlement.
This is the largest model layer in the codebase (~23 modules, 505k tokens).

## Structure

\`\`\`mermaid
graph TD
    Q[question.py Question] -->|has many| O[outcome.py Outcome]
    O -->|price snapshots| OP[outcome_price.py]
    O -->|summary stats| OS[outcome_summary.py]
    Q -->|summary stats| QS[question_summary.py]
    Q -->|categorized by| C[category.py]
    LO[limit_order.py LimitOrder] -->|matched via| OB[order_book.py OrderBook]
    OB -->|produces| MO[match_order.py MatchOrder]
    W[wager.py Wager] -->|actions log| WA[wager_action.py]
    W -->|on outcome| O
\`\`\`

## Key Concepts

- **Question lifecycle** — `Question` extends `DoubleEntryAccount` (has its own
  ledger accounts for each currency) and `IntegrityCheckMixin`. States flow:
  draft → open → closed → resolved/cancelled. Resolution triggers settlement
  of all wager positions.
- **Order book matching** — `OrderBook` (pure Python, no DB model) builds
  normalized bid/ask views from `LimitOrder` querysets. Binary markets mirror
  orders across the two outcomes; multi-outcome markets mirror across positions
  (long/short). `MatchOrder` records each filled trade between a maker and taker.
- **Wager as net position** — `Wager` is one user's consolidated position on one
  outcome in one currency. `WagerAction` logs each purchase/sale with shares,
  amount, and price. The `last_action` JSON field caches the most recent action
  for fast reads.
- **LS-LMSR pricing** — `Question` stores `bounded_loss` and `tax` parameters
  per currency mode. Prices are computed via `contrib.ls_lmsr.LsLmsr` and
  snapshotted in `OutcomePrice` for historical tracking.
- **Shares history** — `shares_history.py` tracks the evolution of outcome
  share quantities over time for charting and analytics.

## Usage

Imported across the entire codebase. The API layer serializes `Question`,
`Outcome`, `Wager`, and `LimitOrder` for the frontend. `importer/` creates and
updates `Question`/`Outcome` from external data sources. `doubleentry/` creates
ledger entries for every wager transaction. `notification/` reads wager state
to send win/loss/cancel notifications.
```

**Why this works:**
- Nested README (wager/models/) zooms in from the parent (wager/) — the parent
  shows the full module flow, the child details the model relationships
- Mermaid uses `graph TD` because this is a data model hierarchy, not a pipeline
- Key Concepts reference actual class names, mixins (`DoubleEntryAccount`,
  `IntegrityCheckMixin`), and implementation details (OrderBook is pure Python,
  not a DB model)
- Quantifies scale ("~23 modules, 505k tokens") to set expectations

---

## Example 3: Identity and auth module (account/)

```markdown
# account

User identity, authentication, KYC verification, and financial account management
for the Futuur prediction market. Handles user registration (email, social, web3/
Privy), OAuth2 token issuance with 2FA, withdrawal requests across multiple
payment gateways, and user summary aggregation for analytics.

## Structure

\`\`\`mermaid
graph LR
    V[views.py] -->|auth + registration| M[models/user.py]
    M -->|aggregates| S[models/user_summary.py]
    M -->|ledger accounts| FA[models/financial_account.py]
    FA -->|withdrawal flow| W[models/withdrawal/]
    T[tasks.py] -->|update summaries| S
    T -->|KYC callbacks| Sumsub[contrib.sumsub]
    choices.py -->|KYC states| M
\`\`\`

## Key Concepts

- **User with DoubleEntryAccount** — `User` extends `AbstractBaseUser` +
  `PermissionsMixin` + `DoubleEntryAccount`, giving each user their own ledger
  accounts per currency. Supports Privy/web3 authentication alongside
  traditional email/social login.
- **UserSummary aggregation** — `UserSummary` caches ~15 aggregate fields
  (total bets, P&L, active country, AB test segments) via `set_data()`,
  updated by Celery tasks grouped by `USER_SUMMARY_UPDATE_GROUPS`.
- **KYC lifecycle** — Users progress through KYC states (NO_NEED → REQUESTED →
  PENDING → APPROVED/REFUSED) defined in `choices.py`. SumSub integration
  handles identity verification callbacks.
- **FinancialAccount** — Bridges users to payment gateways. Each gateway
  (Skrill, Astropay, crypto, etc.) has its own `WithdrawalRequest` subclass
  in `models/withdrawal/`.
- **CustomTokenView** — `views.py` extends OAuth2 token issuance with rate
  limiting, 2FA enforcement, and Mixpanel login tracking.

## Usage

Imported across the entire codebase. The API layer serializes `User` and
`UserSummary` for the frontend. `wager/` checks user balances and geo
restrictions before placing bets. `finance/` processes deposits and
withdrawals through `FinancialAccount`. `notification/` sends KYC and
account-related emails. `analytics/` tracks user segments and access patterns.
```

**Why this works:**
- Title packs in the full scope: identity, auth, KYC, financial accounts,
  analytics — you immediately know this isn't just "user CRUD"
- Mermaid shows distinct flows: auth goes through views → user, summaries are
  async via tasks, withdrawals flow through financial accounts, KYC is a
  separate callback path
- Key Concepts surface non-obvious architecture: User has its own ledger
  accounts (DoubleEntryAccount), UserSummary is a cache layer updated
  asynchronously, KYC has a state machine
- Usage explains *what* each consumer does: wager checks balances, finance
  processes withdrawals, notification sends KYC emails
