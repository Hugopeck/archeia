# Scan Report

> Python / Django 4.2 / pip | 227k LOC | 22 modules | ~2,344k tokens

## Size

| Language   | Files | Lines   |
|------------|-------|---------|
| Python     | 1,894 | 153,098 |
| JavaScript | 23    | 43,559  |
| HTML       | 135   | 12,480  |
| CSS        | 30    | 8,581   |
| SCSS       | 6     | 4,546   |
| Markdown   | 20    | 2,340   |
| JSON       | 10    | 1,117   |
| YAML/YML   | 7     | 498     |
| Text       | 3     | 476     |
| Other      | 92    | —       |
| **Total**  | **2,220** | **226,695** |

## Token Estimates

| Directory      | Est. Tokens | % of Total |
|----------------|-------------|------------|
| wager/         | 505,869     | 21.6%      |
| frontend/      | 477,482     | 20.4%      |
| api/           | 452,097     | 19.3%      |
| reports/       | 113,377     | 4.8%       |
| contrib/       | 200,039     | 8.5%       |
| account/       | 118,233     | 5.0%       |
| importer/      | 102,382     | 4.4%       |
| notification/  | 98,731      | 4.2%       |
| finance/       | 92,343      | 3.9%       |
| doubleentry/   | 38,376      | 1.6%       |
| bot/           | 21,028      | 0.9%       |
| market_maker/  | 21,166      | 0.9%       |
| templates/     | 19,121      | 0.8%       |
| webapp/        | 18,464      | 0.8%       |
| analytics/     | 18,011      | 0.8%       |
| campaign/      | 16,068      | 0.7%       |
| leaderboard/   | 11,336      | 0.5%       |
| docs/          | 7,105       | 0.3%       |
| entity/        | 6,520       | 0.3%       |
| integrity/     | 4,412       | 0.2%       |
| (root)         | 1,735       | 0.1%       |
| formats/       | 183         | <0.1%      |
| locale/        | 0           | 0%         |
| **Total**      | **~2,344k** | **100%**   |

## Structure

```
nagoya-v1/                        (2,220 files)
├── account/                      (251 files)
│   ├── admin/                    (10 files)
│   ├── management/               (15 files)
│   ├── migrations/               (185 files)
│   ├── models/                   (23 files)
│   ├── templates/                (7 files)
│   └── tests/                    (4 files)
├── analytics/                    (44 files)
│   ├── admin/                    (6 files)
│   ├── migrations/               (17 files)
│   ├── models/                   (8 files)
│   └── signals/                  (2 files)
├── api/                          (370 files)
│   ├── migrations/               (3 files)
│   ├── private/                  (5 files)
│   ├── v1/ – v1_5/              (260 files)
│   └── v2_0/                     (86 files)
├── bot/                          (47 files)
│   ├── migrations/               (30 files)
│   └── models/                   (8 files)
├── campaign/                     (52 files)
│   ├── migrations/               (29 files)
│   └── models/                   (5 files)
├── contrib/                      (284 files)
│   ├── astropay/                 (28 files)
│   ├── blockchain/               (8 files)
│   ├── coinpayments/             (14 files)
│   ├── convrtpayments/           (12 files)
│   ├── exchange/                 (27 files)
│   ├── flarum/                   (24 files)
│   ├── futuur/                   (15 files)
│   ├── magic/                    (6 files)
│   ├── model_log/                (12 files)
│   ├── nowpayments/              (8 files)
│   ├── personalize/              (10 files)
│   ├── privy/                    (6 files)
│   ├── pusher_api/               (6 files)
│   ├── rest_framework/           (15 files)
│   ├── skrill/                   (34 files)
│   ├── smartfastpay/             (9 files)
│   └── sumsub/                   (12 files)
├── docs/                         (5 files)
├── doubleentry/                  (84 files)
│   ├── migrations/               (60 files)
│   └── tests/                    (3 files)
├── entity/                       (35 files)
│   ├── migrations/               (27 files)
│   └── models/                   (3 files)
├── finance/                      (93 files)
│   ├── admin/                    (10 files)
│   ├── migrations/               (26 files)
│   ├── models/                   (11 files)
│   ├── payment_gateways/         (13 files)
│   ├── signals/                  (8 files)
│   └── tests/                    (7 files)
├── formats/                      (5 files)
├── frontend/                     (135 files)
│   ├── static/                   (122 files)
│   └── templates/                (10 files)
├── importer/                     (106 files)
│   ├── migrations/               (36 files)
│   ├── models/                   (5 files)
│   └── (data sources)/           (various)
├── integrity/                    (14 files)
├── leaderboard/                  (17 files)
├── locale/                       (2 files)
├── market_maker/                 (29 files)
│   ├── algorithms/               (3 files)
│   └── migrations/               (6 files)
├── notification/                 (113 files)
│   ├── migrations/               (48 files)
│   ├── models/                   (5 files)
│   └── templates/                (42 files)
├── reports/                      (38 files)
│   └── templates/                (24 files)
├── templates/                    (16 files)
├── wager/                        (435 files)
│   ├── admin/                    (13 files)
│   ├── management/               (45 files)
│   ├── migrations/               (300 files)
│   ├── models/                   (23 files)
│   ├── tests/                    (11 files)
│   └── static/                   (16 files)
└── webapp/                       (8 files)
```

## Modules

Django apps (each a top-level directory with its own models/migrations):

| Module         | Files |
|----------------|-------|
| wager          | 435   |
| api            | 370   |
| contrib        | 284   |
| account        | 251   |
| frontend       | 135   |
| notification   | 113   |
| importer       | 106   |
| finance        | 93    |
| doubleentry    | 84    |
| campaign       | 52    |
| bot            | 47    |
| analytics      | 44    |
| reports        | 38    |
| entity         | 35    |
| market_maker   | 29    |
| leaderboard    | 17    |
| templates      | 16    |
| integrity      | 14    |
| webapp         | 8     |
| formats        | 5     |
| docs           | 5     |
| locale         | 2     |

## README Coverage

| Directory                 | Source Files | Has README |
|---------------------------|-------------|------------|
| ./account                 | 7           | No         |
| ./account/admin           | 10          | No         |
| ./account/models          | 18          | No         |
| ./analytics               | 10          | No         |
| ./analytics/admin         | 6           | No         |
| ./analytics/models        | 8           | No         |
| ./api                     | 14          | Yes        |
| ./api/private             | 5           | No         |
| ./bot                     | 5           | No         |
| ./campaign                | 6           | No         |
| ./campaign/models         | 5           | No         |
| ./contrib                 | 29          | No         |
| ./contrib/astropay        | 9           | No         |
| ./contrib/blockchain      | 6           | No         |
| ./contrib/coinpayments    | 9           | No         |
| ./contrib/convrtpayments  | 11          | No         |
| ./contrib/exchange        | 7           | No         |
| ./contrib/flarum          | 9           | No         |
| ./contrib/futuur          | 11          | No         |
| ./contrib/magic           | 6           | No         |
| ./contrib/model_log       | 8           | Yes        |
| ./contrib/nowpayments     | 8           | No         |
| ./contrib/personalize     | 9           | No         |
| ./contrib/pusher_api      | 5           | No         |
| ./contrib/rest_framework  | 11          | No         |
| ./contrib/skrill          | 9           | Yes        |
| ./contrib/smartfastpay    | 9           | No         |
| ./contrib/sumsub          | 9           | No         |
| ./doubleentry             | 5           | No         |
| ./finance                 | 10          | Yes        |
| ./finance/admin           | 10          | No         |
| ./finance/models          | 11          | No         |
| ./finance/payment_gateways| 6          | Yes        |
| ./finance/signals         | 8           | No         |
| ./importer                | 7           | No         |
| ./importer/admin          | 5           | No         |
| ./importer/models         | 5           | No         |
| ./importer/soccerama      | 7           | No         |
| ./integrity               | 9           | No         |
| ./leaderboard             | 8           | No         |
| ./market_maker            | 6           | No         |
| ./notification            | 13          | No         |
| ./notification/models     | 5           | No         |
| ./reports                 | 8           | No         |
| ./templates/admin         | 5           | No         |
| ./wager                   | 11          | No         |
| ./wager/admin             | 13          | No         |
| ./wager/models            | 23          | No         |
| ./wager/tests             | 11          | No         |
| ./webapp                  | 8           | No         |

**5 of 50 directories have READMEs** — 45 directories need READMEs.

## Dependencies

| Manifest         | Direct Deps | Dev Deps |
|------------------|-------------|----------|
| requirements.txt | 91          | —        |
| package.json     | 0           | 1        |

## Test Footprint

- **Test files**: 63
- **Source files** (non-test, non-migration): 1,011
- **Test-to-source ratio**: 0.062 (6.2%)
- **Test framework**: Django test (pytest not detected in requirements.txt; uses Django's built-in test runner)

## Git Vitals

- **Repo age**: 2016-04-19 (10 years)
- **Total commits**: 9,691
- **Contributors**: 23
- **Last commit**: 2026-04-01
- **Remote branches**: 581

## Signals

- **CI workflows**: 3 files — `.circleci/config_PAUSED.yml`, `.github/workflows/deploy.yml`, `.github/workflows/pull_request.yml`
- **Docker**: 1 Dockerfile + 2 docker-compose files (`.deploy/`)
- **TODO/FIXME density**: 123 files contain TODOs — api (49), wager (15), contrib (11), finance (11), account (9), importer (10), notification (5), bot (3), doubleentry (3), webapp (3), market_maker (2), reports (2)
- **Entry points**: `manage.py` (Django), `docs/index.rst`, `templates/admin/index.html`
- **Large files**: 1 file over 1MB — `frontend/static/error-server.gif`
