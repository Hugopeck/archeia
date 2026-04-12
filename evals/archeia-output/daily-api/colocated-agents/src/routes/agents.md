# agents.md — src/routes/

## Rules

- Webhook routes that verify signatures (Paddle, Apple) must explicitly opt in to raw body access — the global `fastify-raw-body` plugin is registered with `global: false`. Add `{ rawBody: true }` to route options and read `request.rawBody` for verification.
- Private routes at `/p` are only registered when `ENABLE_PRIVATE_ROUTES=true`. Do not expose internal endpoints outside this prefix.
- Public REST API rules (auth, rate limiting, OpenAPI) are in `src/routes/public/AGENTS.md` — read that file when working in `routes/public/`.
- Each route module is a Fastify plugin registered with a prefix in `routes/index.ts`. New route groups follow the same pattern: export an async function receiving `FastifyInstance`, register in `index.ts`.
- Do not add business logic to route handlers — delegate to entity queries, common utilities, or trigger Pub/Sub events. Routes are thin controllers.

## README Maintenance

Before working in `src/routes/`, read `src/routes/README.md`.
After completing work, update the README's Learnings section with anything non-obvious discovered.

Maintains: `src/routes/README.md`
