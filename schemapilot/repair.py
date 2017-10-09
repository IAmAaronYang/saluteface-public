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
    repaired_ok: bool
    edits: List[Edit] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_ok": self.original_ok,
            "repaired_ok": self.repaired_ok,
            "edit_count": len(self.edits),
            "edits": [e.to_dict() for e in self.edits],
            "payload": self.payload,
        }


_PATTERN_SEEDS = {
    r"^INV-[0-9]{6}$": "INV-000000",
    r"^[A-Z]{3}$": "USD",
    r"^[a-f0-9]{8}$": "0a1b2c3d",
}


def _pattern_seed(spec: FieldSpec) -> str:
    """Return a value that satisfies a known pattern, else a literal token."""
    if spec.pattern in _PATTERN_SEEDS:
        return _PATTERN_SEEDS[spec.pattern]
    if spec.enum:
        return str(spec.enum[0])
    return "".join(c for c in (spec.pattern or "") if c.isalnum()) or "seed"


def _default_value(spec: FieldSpec) -> Any:
    if spec.has_default:
        return spec.default
    if spec.enum:
        return spec.enum[0]
    return _ZERO.get(spec.type, None)


def _try_coerce(value: Any, ftype: str) -> Any:
    try:
        if ftype == "integer":
            return int(value)
        if ftype == "number":
            return float(value)
        if ftype == "string":
            return str(value)
        if ftype == "boolean":
            if isinstance(value, str):
                return value.strip().lower() in ("true", "1", "yes")
            return bool(value)
    except (TypeError, ValueError):
        return None
    return None

