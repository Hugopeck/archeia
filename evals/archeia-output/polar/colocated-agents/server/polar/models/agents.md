## Local Rules

- All SQLAlchemy models live here, not in domain modules. Do not create model files in `polar/{module}/`.
- Inherit from `polar.kit.db.models.RecordModel` for all new models.
- Use `StringEnum(MyStrEnum)` for state/type columns, not plain `String`.
- Use `MetadataMixin` for models that support user-defined JSONB metadata.
- Use `CustomFieldDataMixin` for models with merchant-defined custom fields.
- Import models via `from polar.models import ModelName`. The `__init__.py` re-exports all models.
- Do not add `created_at`/`modified_at` columns manually; `RecordModel` provides them.
- ForeignKey columns use `Uuid` type with `ForeignKey("tablename.id")`.

## README Maintenance

Before working in this directory, read the README.md.
After completing work, update the README's Learnings section with anything non-obvious you discovered.

Maintains: server/polar/models/README.md
