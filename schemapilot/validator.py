"""Payload validator.

The validator checks a payload against a :class:`~schemapilot.contract.Contract`
and emits a structured :class:`ValidationResult`. Every failure becomes a
:class:`Violation` carrying a stable ``code``, the offending field path, a
human message, and (where relevant) the observed and expected values.

Violation codes
---------------
=====================  ==============================================
Code                   Meaning
=====================  ==============================================
``MISSING_REQUIRED``   a required field is absent
``UNEXPECTED_FIELD``   a field not present in the contract
``TYPE_MISMATCH``      value type does not match the spec
``NULL_NOT_ALLOWED``   explicit null on a non-nullable field
``ENUM_VIOLATION``     scalar not in the declared enum
``BELOW_MIN``          numeric below inclusive minimum
``ABOVE_MAX``          numeric above inclusive maximum
``TOO_SHORT``          string shorter than ``min_len``
``TOO_LONG``           string longer than ``max_len``
``PATTERN_MISMATCH``   string fails the anchored pattern
``TOO_FEW_ITEMS``      array shorter than ``min_items``
``TOO_MANY_ITEMS``     array longer than ``max_items``
``ITEM_INVALID``       an array element failed nested validation
=====================  ==============================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from schemapilot.contract import Contract, FieldSpec

_PY_TYPE = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


@dataclass
class Violation:
    code: str
    path: str
    message: str
    observed: Any = None
    expected: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "path": self.path,
            "message": self.message,
            "observed": self.observed,
            "expected": self.expected,
        }


@dataclass
class ValidationResult:
    ok: bool
    violations: List[Violation] = field(default_factory=list)

    @property
    def codes(self) -> List[str]:
        return [v.code for v in self.violations]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "violation_count": len(self.violations),
            "violations": [v.to_dict() for v in self.violations],
        }


def _type_ok(value: Any, ftype: str) -> bool:
    if ftype == "null":
        return value is None
    if ftype == "integer":
        # bool is a subclass of int; reject it for integer fields.
        return isinstance(value, int) and not isinstance(value, bool)
    if ftype == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if ftype == "boolean":
        return isinstance(value, bool)
    expected = _PY_TYPE.get(ftype)
    return expected is not None and isinstance(value, expected)


class Validator:
    """Validate payloads against a contract."""

    def __init__(self, contract: Contract, *, allow_extra: bool = False) -> None:
        self.contract = contract
        self.allow_extra = allow_extra

    def validate(self, payload: Dict[str, Any]) -> ValidationResult:
        violations: List[Violation] = []

