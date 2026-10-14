"""Protein-sequence parsing and normalization, using strict standard amino-acid codes."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from .errors import InvalidSequence

ALPHABET = frozenset("ACDEFGHIKLMNPQRSTVWY")


def normalize_sequence(value: str, *, strip_whitespace: bool = True) -> str:
    if not isinstance(value, str):
        raise InvalidSequence("sequence must be text")
    if strip_whitespace:
        value = "".join(value.split())
    return value.upper()


def validate_sequence(value: str, *, min_length: int = 1, max_length: int = 100_000) -> str:
    sequence = normalize_sequence(value)
    if not min_length <= len(sequence) <= max_length:
        raise InvalidSequence(f"length {len(sequence)} outside [{min_length}, {max_length}]")
    invalid = set(sequence) - ALPHABET
    if invalid:
        raise InvalidSequence("invalid residues: " + "".join(sorted(invalid)))
    return sequence


def gc_like_composition(sequence: str) -> dict[str, float]:
    """Residue frequencies (not nucleic-acid GC content)."""
    sequence = validate_sequence(sequence)
    count = Counter(sequence)
    return {aa: count[aa] / len(sequence) for aa in sorted(ALPHABET)}


@dataclass(frozen=True)
class SequenceRecord:
    identifier: str
    sequence: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.identifier or any(ch.isspace() for ch in self.identifier):
            raise InvalidSequence("identifier must be a nonempty single token")
        object.__setattr__(self, "sequence", validate_sequence(self.sequence))
