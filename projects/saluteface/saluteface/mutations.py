"""Deterministic adversarial sequence perturbations for non-biological tests.

Mutations are synthetic; they do not preserve protein function.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import random
from .sequence import ALPHABET, validate_sequence

@dataclass(frozen=True)
class Mutation:
    kind: str
    source: str
    result: str
    seed: int
    edits: int

def _rng(seed: int, identifier: str) -> random.Random:
    digest = hashlib.sha256(f"{seed}:{identifier}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))

def substitute(sequence: str, count: int, *, seed: int = 0, identifier: str = "") -> Mutation:
    original = validate_sequence(sequence)
    if count < 0 or count > len(original):
        raise ValueError("substitutions outside sequence length")
    rng = _rng(seed, identifier)
    chars = list(original)
    for index in rng.sample(range(len(chars)), count):
        options = sorted(ALPHABET - {chars[index]})
        chars[index] = rng.choice(options)
    return Mutation("substitution", original, "".join(chars), seed, count)

def deletion(sequence: str, count: int, *, seed: int = 0, identifier: str = "") -> Mutation:
    original = validate_sequence(sequence)
    if count < 0 or count >= len(original):
        raise ValueError("deletion count must be smaller than length")
    rng = _rng(seed, identifier)
    positions = set(rng.sample(range(len(original)), count))
    return Mutation("deletion", original, "".join(c for i, c in enumerate(original) if i not in positions), seed, count)

def insertion(sequence: str, count: int, *, seed: int = 0, identifier: str = "") -> Mutation:
    original = validate_sequence(sequence)
    if count < 0 or len(original) + count > 100_000:
        raise ValueError("invalid insertion count")
    rng = _rng(seed, identifier)
    chars = list(original)
    for _ in range(count):
        chars.insert(rng.randrange(len(chars) + 1), rng.choice(sorted(ALPHABET)))
    return Mutation("insertion", original, "".join(chars), seed, count)

def perturb(sequence: str, kind: str, count: int, *, seed: int = 0, identifier: str = "") -> Mutation:
    methods = {"substitution": substitute, "deletion": deletion, "insertion": insertion}
    if kind not in methods:
        raise ValueError(f"unknown perturbation kind: {kind}")
    return methods[kind](sequence, count, seed=seed, identifier=identifier)
