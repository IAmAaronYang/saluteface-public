"""Sequence features for exploratory research; no biological effect claims."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, asdict
from math import log2
from .sequence import ALPHABET, validate_sequence

@dataclass(frozen=True)
class SequenceFeatures:
    length: int
    distinct_residues: int
    entropy_bits: float
    top_residue: str
    top_fraction: float
    kmer_diversity: float
    homopolymer_max: int
    hydrophobic_fraction: float

def kmers(sequence: str, k: int) -> dict[str, int]:
    seq = validate_sequence(sequence)
    if k < 1 or k > len(seq):
        raise ValueError("k must be between 1 and sequence length")
    return dict(sorted(Counter(seq[i:i+k] for i in range(len(seq)-k+1)).items()))

def shannon_entropy(sequence: str) -> float:
    seq = validate_sequence(sequence)
    counts = Counter(seq)
    return -sum((n/len(seq)) * log2(n/len(seq)) for n in counts.values())

def longest_run(sequence: str) -> int:
    seq = validate_sequence(sequence)
    longest = current = 1
    for i in range(1, len(seq)):
        current = current+1 if seq[i] == seq[i-1] else 1
        longest = max(longest, current)
    return longest

def extract_features(sequence: str, *, k: int = 3) -> SequenceFeatures:
    seq = validate_sequence(sequence)
    counts = Counter(seq)
    name, freq = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[0]
    words = kmers(seq, min(k, len(seq)))
    return SequenceFeatures(len(seq), len(counts), shannon_entropy(seq), name, freq/len(seq),
        len(words)/sum(words.values()), longest_run(seq), sum(c in "AVILMFWY" for c in seq)/len(seq))

def feature_dict(sequence: str, *, k: int = 3) -> dict[str, object]:
    return asdict(extract_features(sequence, k=k))
