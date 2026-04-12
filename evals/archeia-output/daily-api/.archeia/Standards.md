# Standards

## Language and Runtime

- **Language:** TypeScript 5.x with strict mode enabled (`"strict": true`, `"strictPropertyInitialization": false`)
- **Target:** ES2019 / CommonJS modules
- **Runtime:** Node.js 22 (pinned in `.nvmrc`)
- **Decorators:** `experimentalDecorators` and `emitDecoratorMetadata` enabled for TypeORM and class-based entities

**Evidence:** `tsconfig.json`, `.nvmrc`

## Formatting

- **Formatter:** Prettier, configured via `.prettierrc`
- **Integration:** `eslint-plugin-prettier` enforces formatting as ESLint errors (`"prettier/prettier": "error"`)
- Run: `pnpm run lint` (lint includes format checks)

**Evidence:** `.prettierrc`, `.eslintrc.js`

## Linting

- **Linter:** ESLint with `@typescript-eslint/eslint-plugin` + `@typescript-eslint/parser`
- **Key rules:**
  - `unused-imports/no-unused-imports: error` — no unused imports
  - `no-restricted-imports` — `isWeekend` from `date-fns` must be imported from `src/common` instead
  - Schema files (`src/schema/*.ts`): `traceResolvers` must NOT be imported directly; it is applied centrally in `src/graphql.ts`
  - Migration files: `@typescript-eslint/no-explicit-any` is disabled
- Run: `pnpm run lint`

**Evidence:** `.eslintrc.js`

## Type Checking

- TypeScript type checking is enforced at build time (`pnpm build`) and in CI
- `ts-jest` is used for test compilation but type diagnostics are excluded during test runs
- `skipLibCheck: true` is set to speed up compilation

**Evidence:** `tsconfig.json`, `jest.config.js`

## Testing

- **Framework:** Jest 29.x with `ts-jest` preset
- **Test directory:** `__tests__/` (excluded from `tsconfig.json` build)
- **Pattern:** Test files in `__tests__/` mirror the `src/` structure
- **Setup:** `__tests__/setup.ts` (runs before each test file), `__tests__/teardown.ts` (global teardown)
- **Environment:** `testEnvironment: node`, `TZ=UTC` forced via `jest.config.js`
- **Run tests:** `pnpm run test` (requires `NODE_ENV=test` and a running PostgreSQL at `api_test` database via `docker-compose`)
- **Prerequisite:** `pnpm run pretest` runs `db:migrate:reset` before tests
- Worker idle memory limit: 2048MB per worker

**Evidence:** `jest.config.js`, `package.json`

## Naming Conventions

- **Entities** (`src/entity/`): PascalCase file names matching the class name (e.g., `User.ts`, `ArticlePost.ts`)
- **Schema resolvers** (`src/schema/`): kebab-case or camelCase file names (e.g., `feeds.ts`, `dataLoaderService.ts`)
- **Workers** (`src/workers/`): camelCase file names (e.g., `newView.ts`, `postUpvotedRep.ts`)
- **Mixed patterns:** PascalCase dominant in `entity/`, camelCase/kebab elsewhere

**Evidence:** `src/entity/index.ts`, `src/workers/index.ts`

## Import Restrictions

- `isWeekend` from `date-fns` — import from `src/common` instead
- `traceResolvers` — do not import in individual schema files; it is applied centrally in `src/graphql.ts`
- Unused imports are an error (enforced by `unused-imports/no-unused-imports`)

**Evidence:** `.eslintrc.js`

## Database Migrations

- All schema changes go through TypeORM migrations in `src/migration/`
- Generate: `pnpm run db:migrate:make`
- Apply: `pnpm run db:migrate:latest`
- Rollback: `pnpm run db:migrate:rollback`
- 479 migration files as of the current snapshot

**Evidence:** `package.json`, `src/data-source.ts`

## CI/CD

- **Primary CI:** CircleCI (`.circleci/config.yml`)
- **GitHub Actions:** Claude code review (`claude.yml`), CodeQL security scan (`codeql-analysis.yml`), Jira ticket linking (`comment-jira-ticket.yml`)
- **Pre-commit hooks:** Not configured

**Evidence:** `.circleci/config.yml`, `.github/workflows/`
