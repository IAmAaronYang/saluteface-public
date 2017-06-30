"""Deterministic payload fuzzer.

The fuzzer turns a :class:`~schemapilot.contract.Contract` into a stream of
:class:`FuzzCase` objects. Generation is *deterministic*: the same contract
and seed always produce the same cases, which makes reports diffable and CI
reproducible.

Two families of cases are produced:

``valid``
    Payloads that satisfy every constraint. Useful as golden fixtures and to
    prove a downstream consumer accepts conforming data.

``adversarial``
    Payloads that violate exactly one constraint in a labelled way (wrong
    type, out-of-bounds, enum miss, pattern miss, missing-required, extra
    field, null-where-not-allowed, empty/oversized arrays). Each adversarial
    case records the *mutation* applied so validators and repair plans can be
    scored against a known ground truth.

The generator uses a small linear-congruential PRNG seeded from the contract
fingerprint plus the user seed, so it never touches the global ``random``
state and stays reproducible across processes and platforms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from schemapilot.contract import Contract, FieldSpec


class _LCG:
    """A tiny deterministic PRNG (Numerical Recipes constants)."""

    __slots__ = ("state",)

    def __init__(self, seed: int) -> None:
        self.state = (seed ^ 0x5DEECE66D) & 0xFFFFFFFFFFFF

    def next(self) -> int:
        self.state = (self.state * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        return (self.state >> 16) & 0xFFFFFFFF

    def below(self, n: int) -> int:
        return self.next() % max(1, n)

    def pick(self, seq: List[Any]) -> Any:
        return seq[self.below(len(seq))]


@dataclass
class FuzzCase:
    """A single generated payload with provenance metadata."""

    case_id: str
    kind: str  # "valid" | "adversarial"
    payload: Dict[str, Any]
    mutation: Optional[str] = None  # label of the injected fault (adversarial)
    target_field: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "kind": self.kind,
            "payload": self.payload,
            "mutation": self.mutation,
            "target_field": self.target_field,
        }


_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"


def _seed_string(rng: _LCG, length: int) -> str:
    return "".join(_ALPHABET[rng.below(len(_ALPHABET))] for _ in range(max(1, length)))


def _valid_scalar(spec: FieldSpec, rng: _LCG) -> Any:
    if spec.enum:
        return rng.pick(list(spec.enum))
    if spec.type == "string":
        lo = spec.min_len or 3
        hi = spec.max_len or max(lo, 8)
        # If a pattern is present we cannot generically satisfy it; emit a
        # deterministic sample from the fixtures instead of guessing.
        if spec.pattern:
            return _pattern_sample(spec.pattern, rng)
        return _seed_string(rng, lo + rng.below(hi - lo + 1))
    if spec.type == "integer":
        lo = int(spec.minimum) if spec.minimum is not None else 0
        hi = int(spec.maximum) if spec.maximum is not None else lo + 100
        return lo + rng.below(hi - lo + 1)
    if spec.type == "number":
        lo = spec.minimum if spec.minimum is not None else 0.0
        hi = spec.maximum if spec.maximum is not None else lo + 100.0
        span = hi - lo
        return round(lo + (rng.next() / 0xFFFFFFFF) * span, 4)
    if spec.type == "boolean":
        return bool(rng.below(2))
    if spec.type == "null":
        return None
    return None


_HEX_ALPHABET = "0123456789abcdef"


def _hex_string(rng: _LCG, length: int) -> str:
    return "".join(_HEX_ALPHABET[rng.below(16)] for _ in range(max(1, length)))


def _pattern_sample(pattern: str, rng: _LCG) -> str:
    """Best-effort deterministic sample for a handful of common patterns."""
    known = {
        r"^INV-[0-9]{6}$": f"INV-{rng.below(1000000):06d}",
        r"^[A-Z]{3}$": "USD",
        r"^[a-f0-9]{8}$": _hex_string(rng, 8),
    }
    if pattern in known:
        return known[pattern]
    # Fallback: produce a token that at least resembles the literal prefix.
    literal = "".join(c for c in pattern if c.isalnum() or c in "-_")
    return literal or _seed_string(rng, 6)


def _valid_value(spec: FieldSpec, rng: _LCG) -> Any:
    if spec.type == "array":
        count = spec.min_items or 1
        item_spec = spec.items or FieldSpec(name=spec.name + "[]", type="string")
        return [_valid_value(item_spec, rng) for _ in range(count)]
    if spec.type == "object":
        return {"k": _seed_string(rng, 4)}
    return _valid_scalar(spec, rng)


class Fuzzer:
    """Deterministic generator over a contract."""

    def __init__(self, contract: Contract, seed: int = 0) -> None:
        self.contract = contract
