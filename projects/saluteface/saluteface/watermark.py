"""Educational sequence watermark experiment.

This is an original, transparent toy protocol, NOT a reproduction or implementation
of Google DeepMind's SynthID Bio. It is not robust against sequence modifications
and is unsuitable as proof of origin or biological attribution.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import hmac
from .sequence import validate_sequence

# Conservative educational substitutions selected for demonstration only.
PAIRS = {"A": "G", "G": "A", "D": "E", "E": "D", "I": "L", "L": "I", "K": "R", "R": "K", "S": "T", "T": "S", "V": "M", "M": "V"}
ORDERED = tuple(sorted(PAIRS))


@dataclass(frozen=True)
class Verification:
    detected: bool
    positions: int
    matches: int
    agreement: float
    note: str = "Educational demonstration; not evidence of provenance"


class WatermarkCodec:
    """Keyed positional experiment with a fixed reversible substitution palette.

    Embedding will alter primary sequence. Never feed resulting sequences to
    biological experiments, model training or claims of preserved function.
    """

    def __init__(self, key: bytes, *, stride: int = 7, threshold: float = 0.90):
        if not key or not isinstance(key, bytes):
            raise ValueError("nonempty byte key required")
        if stride < 2:
            raise ValueError("stride must be >= 2")
        if not (0 < threshold <= 1):
            raise ValueError("threshold out of range")
        self.key, self.stride, self.threshold = key, stride, threshold

    def _desired(self, index: int) -> str:
        digest = hmac.new(self.key, str(index).encode(), hashlib.sha256).digest()
        return ORDERED[digest[0] % len(ORDERED)]

    def embed(self, sequence: str) -> str:
        seq = list(validate_sequence(sequence))
        for i in range(0, len(seq), self.stride):
            desired = self._desired(i)
            if seq[i] in PAIRS:
                seq[i] = desired
        return "".join(seq)

    def verify(self, sequence: str) -> Verification:
        seq = validate_sequence(sequence)
        positions = [i for i in range(0, len(seq), self.stride) if seq[i] in PAIRS]
        matches = sum(seq[i] == self._desired(i) for i in positions)
        agreement = matches / len(positions) if positions else 0.0
        return Verification(bool(positions) and agreement >= self.threshold, len(positions), matches, agreement)
