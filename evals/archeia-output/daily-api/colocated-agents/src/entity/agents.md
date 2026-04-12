# agents.md — src/entity/

## Rules

- When adding a new entity subtype (Post or Source), use `@ChildEntity()` on the class and define only the subtype-specific columns. Shared columns go on the base entity.
- Never add new columns without generating a TypeORM migration: `pnpm run db:migrate:make src/migration/DescriptiveName`.
- JSONB flags columns (`PostFlags`, `UserFlags`, `SourceFlagsPublic`) must be typed via the exported `Partial<{...}>` type. Never read raw JSONB keys directly.
- Post IDs are `text` (external crawler IDs). User IDs are `varchar(36)` (UUID). Comment IDs are `varchar(14)` (nanoid). Do not assume consistent ID formats across entity types.
- Most relations use `lazy: true` — they return `Promise<T>`. Await them explicitly or use GraphORM for eager loading via field selection. Never access a lazy relation without `await`.
- Do not set `synchronize: true` — schema sync is disabled in all environments. All schema changes must go through migrations.
- Migration files in `src/migration/` may use `any` — `@typescript-eslint/no-explicit-any` is relaxed there by ESLint config.

## README Maintenance

Before working in `src/entity/` or its subdirectories, read `src/entity/README.md`.
After completing work, update the README's Learnings section with anything non-obvious discovered.

Maintains: `src/entity/README.md`
