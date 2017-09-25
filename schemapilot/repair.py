"""Minimal repair engine.

Given a contract and an invalid payload, :func:`repair_payload` computes a
:class:`RepairPlan`: an ordered list of concrete edits that would make the
payload conform, plus the repaired payload itself. The engine favours the
*smallest* change that resolves each violation:

- ``MISSING_REQUIRED`` -> insert the field's ``default`` when present, else a
  type-appropriate zero value.
- ``UNEXPECTED_FIELD``  -> drop the field.
- ``NULL_NOT_ALLOWED``  -> replace null with ``default`` or a zero value.
- ``TYPE_MISMATCH``     -> coerce when safely possible (e.g. ``"12"`` -> 12),
  otherwise substitute a zero value.
- ``ENUM_VIOLATION``    -> snap to the first enum member.
- ``BELOW_MIN``/``ABOVE_MAX`` -> clamp to the nearest bound.
- ``TOO_SHORT``/``TOO_LONG``  -> pad or truncate the string.
- ``TOO_FEW_ITEMS``/``TOO_MANY_ITEMS`` -> pad or trim the array.

Each repair is described by an :class:`Edit` so callers can present a diff and
audit the transformation. The engine re-validates after applying edits and
reports whether the payload is now conforming.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from schemapilot.contract import Contract, FieldSpec
from schemapilot.validator import Validator, Violation

_ZERO = {
    "string": "",
    "integer": 0,
    "number": 0.0,
    "boolean": False,
    "array": [],
    "object": {},
    "null": None,
}


@dataclass
class Edit:
    op: str  # "insert" | "delete" | "replace" | "clamp" | "coerce" | "truncate" | "pad"
    path: str
    before: Any = None
    after: Any = None
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op": self.op,
            "path": self.path,
            "before": self.before,
            "after": self.after,
            "reason": self.reason,
        }


@dataclass
class RepairPlan:
    original_ok: bool
