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

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"type": self.type}
        if self.required:
            out["required"] = True
        if self.nullable:
            out["nullable"] = True
        if self.enum is not None:
            out["enum"] = self.enum
        if self.minimum is not None:
            out["min"] = self.minimum
        if self.maximum is not None:
            out["max"] = self.maximum
        if self.min_len is not None:
            out["min_len"] = self.min_len
        if self.max_len is not None:
            out["max_len"] = self.max_len
        if self.pattern is not None:
            out["pattern"] = self.pattern
        if self.min_items is not None:
            out["min_items"] = self.min_items
        if self.max_items is not None:
            out["max_items"] = self.max_items
        if self.items is not None:
            out["items"] = self.items.to_dict()
        if self.has_default:
            out["default"] = self.default
        return out


@dataclass
class Contract:
    """A parsed, validated contract."""

    name: str
    version: int
    fields: Dict[str, FieldSpec] = field(default_factory=dict)

    @property
    def field_names(self) -> List[str]:
        return list(self.fields.keys())

    @property
    def required_fields(self) -> List[str]:
        return [n for n, f in self.fields.items() if f.required]

    def fingerprint(self) -> str:
        """A stable, order-independent digest of the contract structure."""
        import hashlib

        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "fields": {n: f.to_dict() for n, f in self.fields.items()},
        }


def _parse_field(name: str, raw: Dict[str, Any]) -> FieldSpec:
    if not isinstance(raw, dict):
        raise ContractError(f"field '{name}' must be an object")
    ftype = raw.get("type")
    if ftype not in ALL_TYPES:
        raise ContractError(f"field '{name}' has unknown type {ftype!r}")

    items = None
    if "items" in raw:
        if ftype != "array":
            raise ContractError(f"field '{name}' uses 'items' but is not an array")
        items = _parse_field(f"{name}[]", raw["items"])

    spec = FieldSpec(
        name=name,
        type=ftype,
        required=bool(raw.get("required", False)),
        nullable=bool(raw.get("nullable", False)),
        enum=raw.get("enum"),
        minimum=raw.get("min"),
        maximum=raw.get("max"),
        min_len=raw.get("min_len"),
        max_len=raw.get("max_len"),
        pattern=raw.get("pattern"),
        min_items=raw.get("min_items"),
        max_items=raw.get("max_items"),
        items=items,
    )
    if "default" in raw:
        spec.default = raw["default"]
        spec.has_default = True

    _sanity_check(spec)
    return spec


def _sanity_check(spec: FieldSpec) -> None:
    if spec.minimum is not None and spec.maximum is not None:
        if spec.minimum > spec.maximum:
            raise ContractError(f"field '{spec.name}': min > max")
    if spec.min_len is not None and spec.max_len is not None:
        if spec.min_len > spec.max_len:
            raise ContractError(f"field '{spec.name}': min_len > max_len")
    if spec.min_items is not None and spec.max_items is not None:
        if spec.min_items > spec.max_items:
            raise ContractError(f"field '{spec.name}': min_items > max_items")
    if spec.pattern is not None:
        try:
            re.compile(spec.pattern)
        except re.error as exc:  # pragma: no cover - defensive
            raise ContractError(f"field '{spec.name}': bad pattern: {exc}") from exc


def load_contract(source: Any) -> Contract:
    """Load a contract from a dict, JSON string, or file path.

    Parameters
    ----------
    source:
        A ``dict`` already parsed, a ``str``/``Path`` pointing at a JSON file,
        or a raw JSON ``str`` beginning with ``{``.
    """
    if isinstance(source, Contract):
        return source
    if isinstance(source, (str, Path)):
        text = str(source)
        if isinstance(source, Path) or (not text.lstrip().startswith("{")):
            text = Path(source).read_text(encoding="utf-8")
        data = json.loads(text)
    elif isinstance(source, dict):
        data = source
    else:
        raise ContractError(f"cannot load contract from {type(source).__name__}")

    if "name" not in data or "fields" not in data:
        raise ContractError("contract requires 'name' and 'fields'")
    fields = {
        name: _parse_field(name, raw) for name, raw in data["fields"].items()
    }
    return Contract(
        name=str(data["name"]),
        version=int(data.get("version", 1)),
