"""Report emitters.

SchemaPilot produces two report formats from a fuzz+validate run:

- **JSON** — a machine-readable envelope for CI gates and dashboards.
- **Markdown** — a human-readable summary with tables, suitable for PR
  comments and release notes.

Both formats are derived from the same in-memory :class:`RunReport` so the
two never drift.
"""

