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
``boolean``, ``array``, ``object``, ``null``.

Constraints understood by the validator and fuzzer:

===============  ================================================
Constraint       Applies to
===============  ================================================
``required``     any field (default ``false``)
``enum``         any scalar type
``min``/``max``  ``integer``, ``number`` (inclusive bounds)
``min_len``      ``string`` (character count, inclusive)
``max_len``      ``string`` (character count, inclusive)
``pattern``      ``string`` (Python ``re`` anchored fullmatch)
``min_items``    ``array`` (inclusive)
``max_items``    ``array`` (inclusive)
``items``        ``array`` (nested :class:`FieldSpec`)
``default``      any field (used by repair engine)
``nullable``     any field (allows an explicit ``null`` value)
===============  ================================================
"""

from __future__ import annotations

import json
import re
