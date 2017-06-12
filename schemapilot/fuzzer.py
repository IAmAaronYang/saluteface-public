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
