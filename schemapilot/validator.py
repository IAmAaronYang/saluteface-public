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


