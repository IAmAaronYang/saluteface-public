"""Contract model and parser.

A SchemaPilot *contract* is a compact JSON object describing the shape of a
structured output. It intentionally uses a small, opinionated vocabulary so
that contracts stay readable and diffable in code review.

Contract grammar (informal)::

    {
      "name": "invoice.v1",
      "version": 1,
      "fields": {
        "id":        {"type": "string", "pattern": "^INV-[0-9]{6}$", "required": true},
        "total":     {"type": "number", "min": 0, "max": 1e9, "required": true},
        "currency":  {"type": "string", "enum": ["USD", "EUR", "GBP"]},
        "lines":     {"type": "array", "min_items": 1, "max_items": 500,
                       "items": {"type": "object"}},
        "paid":      {"type": "boolean", "default": false}
      }
    }

Supported field ``type`` values: ``string``, ``integer``, ``number``,
