---
source: .archeia/codebase/architecture/dataflow.json
mermaid_type: sequenceDiagram
message_limit: 10
depends_on: DataFlow.json
condition: DataFlow.json exists
validation: all-participants-trace-to-json, all-messages-trace-to-steps, arrow-types-match-step-types, message-limit-respected
---

## Purpose

The Primary Sequence diagram answers: **how does a request flow through the
system end to end?**

It renders the primary flow from DataFlow.json as a visual sequence of messages
between participants. Each step in the JSON becomes one message. Participants
are containers, components, people, or external systems from the C4 model. The
diagram shows the most common request path — the one use case that exercises
the most of the system.

---

## Mapping Rules

1. **Find the primary flow.** Scan `flows` for the entry with
   `"primary": true`. If no flow is marked primary, use the first flow in
   the array.

2. **Participants.** Each entry in the flow's `participants` becomes a
   participant declaration. Use `id` as the Mermaid participant ID and `name`
   as the display alias:
   ```
   participant end-user as End User
   participant api-server as API Server
   ```

3. **Messages.** Each entry in `steps`, ordered by `order`, becomes a message.
   The arrow type depends on `type`:
   - `sync` → `->>` (solid arrow with arrowhead)
   - `async` → `-)` (solid arrow with open arrowhead)
   - `response` → `-->>` (dashed arrow with arrowhead)

   Format: `source_id->>target_id: message`

4. **Message limit enforcement.** If the flow has more than 10 steps, include
   the first 10 by `order`. Log which steps were omitted.

5. **Additional flows.** If DataFlow.json contains non-primary flows, generate
   a separate file for each: `sequence-[flow-id].md`. Apply the same rules.
   Use the flow's `name` in the heading: `# Sequence — [flow name]`.

---

## Participant ID Convention

Sequence diagrams use the **raw `id`** from the JSON as the participant
identifier. No UPPER_SNAKE_CASE conversion — Mermaid sequence participants
handle hyphens and lowercase correctly. The `name` field becomes the display
alias via `participant id as Name`.

---

## Arrow Convention

| Step Type | Arrow | Meaning | Example |
|-----------|-------|---------|---------|
| `sync` | `->>` | Synchronous call (caller blocks) | `api-server->>postgresql: INSERT task` |
| `async` | `-)` | Asynchronous (fire-and-forget, queue) | `api-server-)background-worker: enqueue job` |
| `response` | `-->>` | Return path of a prior sync call | `postgresql-->>api-server: task record` |

---

## Example Transformation

**Input** (`.archeia/codebase/architecture/dataflow.json`, primary flow):

```json
{
  "flows": [
    {
      "id": "create-task",
      "name": "Create Task",
      "primary": true,
      "participants": [
        { "id": "end-user", "name": "End User", "type": "person" },
        { "id": "api-server", "name": "API Server", "type": "container" },
        { "id": "api-services", "name": "Task Service", "type": "component" },
        { "id": "postgresql", "name": "PostgreSQL", "type": "external_system" },
        { "id": "background-worker", "name": "Background Worker", "type": "container" }
      ],
      "steps": [
        { "order": 1, "source": "end-user", "target": "api-server", "message": "POST /tasks {title, description}", "type": "sync" },
        { "order": 2, "source": "api-server", "target": "api-services", "message": "createTask(data)", "type": "sync" },
        { "order": 3, "source": "api-services", "target": "postgresql", "message": "INSERT task", "type": "sync" },
        { "order": 4, "source": "api-services", "target": "api-server", "message": "task record", "type": "response" },
        { "order": 5, "source": "api-server", "target": "end-user", "message": "201 Created", "type": "response" },
        { "order": 6, "source": "api-server", "target": "background-worker", "message": "enqueue notification job", "type": "async" }
      ]
    }
  ]
}
```

**Output** (`.archeia/codebase/diagrams/sequence-primary.md`):

````markdown
# Primary Sequence — Create Task

```mermaid
sequenceDiagram
    participant end-user as End User
    participant api-server as API Server
    participant api-services as Task Service
    participant postgresql as PostgreSQL
    participant background-worker as Background Worker

    end-user->>api-server: POST /tasks {title, description}
    api-server->>api-services: createTask(data)
    api-services->>postgresql: INSERT task
    api-services-->>api-server: task record
    api-server-->>end-user: 201 Created
    api-server-)background-worker: enqueue notification job
```

**Source:** `.archeia/codebase/architecture/dataflow.json` (flow: create-task)
**Generated:** 2025-01-15
````

---

## Quality Rubric

- **TRACEABILITY:** Every participant traces to an entry in the flow's
  `participants` array. Every message traces to an entry in `steps`. No
  invented interactions.
- **COMPLETENESS:** All participants from the primary flow appear. All steps
  appear as messages in order. Response steps are included (they show the
  return path).
- **LABELING:** Every message has the `message` text from the step. Arrow
  types correctly match `type` (sync/async/response).
- **LIMITS:** Total message count does not exceed 10. When trimming, include
  the first 10 steps by `order` and log omissions.

---

## Anti-Patterns

- **Inventing response steps.** If the JSON has 6 steps, the diagram has 6
  messages. Do not add implicit returns that aren't in the data.
- **Using the wrong arrow type.** Async messages use `-)`, not `->>`. Response
  messages use `-->>`, not `->>`. The distinction matters visually.
- **Exceeding 10 messages.** Long sequences become unreadable. If the flow
  has 15 steps, include the first 10 and note the omission.
- **Converting participant IDs to UPPER_SNAKE_CASE.** Sequence diagrams use
  raw IDs — the `as Name` alias handles display.
