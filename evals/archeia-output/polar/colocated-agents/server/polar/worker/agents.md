## Local Rules

- Worker files prefixed with `_` are internal infrastructure. Do not modify without understanding the broker lifecycle.
- Use `enqueue_job("task.name", arg=value)` to dispatch jobs from services. Never call dramatiq actors directly.
- Worker sessions auto-commit on success and rollback on failure. Do not call `session.commit()`.
- Use `_debounce.py` patterns when a job should not run more than once within a time window.
- `_queues.py` defines named queues with different priorities. Use `TaskPriority` enum when defining actors.
- The scheduler (`scheduler.py`) uses APScheduler. Add periodic tasks there, not as cron jobs.

## README Maintenance

Before working in this directory, read the README.md.
After completing work, update the README's Learnings section with anything non-obvious you discovered.

Maintains: server/polar/worker/README.md
