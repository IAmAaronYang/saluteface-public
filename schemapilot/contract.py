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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

SCALAR_TYPES = {"string", "integer", "number", "boolean", "null"}
ALL_TYPES = SCALAR_TYPES | {"array", "object"}


class ContractError(ValueError):
    """Raised when a contract document is malformed."""


@dataclass
class FieldSpec:
    """A single field's specification within a contract."""

    name: str
    type: str
    required: bool = False
    nullable: bool = False
    enum: Optional[List[Any]] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    min_len: Optional[int] = None
    max_len: Optional[int] = None
    pattern: Optional[str] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    items: Optional["FieldSpec"] = None
    default: Any = None
    has_default: bool = False

    @property
    def compiled_pattern(self) -> Optional["re.Pattern[str]"]:
        if self.pattern is None:
            return None
        return re.compile(self.pattern)

