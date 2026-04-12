# Task Authoring

Repo-specific task specs are authored in `evals/config/tasks/<repo-id>/` using
the schema in `task-template.yaml`.

These task files are **Phase 2 preparation artifacts**. They are inputs to the
evaluation harness and must be grounded before Phase 3 runs the real Archeia
pipeline to generate canonical bundles.

## Authoring rules

- Keep prompts realistic and avoid telling the agent which file to edit.
- Use one file per task.
- Ground every task in an actual pinned repo checkout.
- Write acceptance criteria and ground truth before running the eval.
- Prefer broad `expected_modules_read` hints over single-file spoilers.
- Use filenames and `id` values in the form `<repo-id>-<category>-<nn>`.
- Standardize `metadata` with: `difficulty`, `output_type`, `primary_surface`,
  `doc_sensitivity`, and `verification_scope`.
- Do not mention Archeia, docs, or evaluation conditions in the task prompt.

## Minimum fields

- `id`
- `repo_id`
- `category`
- `prompt`
- `ground_truth`
- `acceptance_criteria`

## Recommended fields

- `expected_modules_read`
- `commands`
- `metadata.difficulty`
- `metadata.output_type`
- `metadata.primary_surface`
- `metadata.doc_sensitivity`
- `metadata.verification_scope`

## Suggested workflow

1. Open the pinned repo from `evals/config/repos.yaml`.
2. Confirm the task is grounded at the pinned commit.
3. Write the prompt, ground truth, and acceptance criteria.
4. Add `expected_modules_read` as broad but useful targeting hints.
5. Use repo default `commands` unless a task-specific override is safer.
6. Save the task JSON/YAML under `evals/config/tasks/<repo-id>/`.

## Phase 2 completion checks

- Every repo has 10 tasks: 2 ask, 2 plan, 2 implement-simple, 2
  implement-moderate, and 2 implement-complex.
- `id` matches the filename stem.
- `repo_id` matches the containing directory.
- Ground truth names real modules or subsystems from the pinned repo.
- No prompt spoils the exact file to edit.
