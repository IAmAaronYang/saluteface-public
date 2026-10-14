"""Dataset QC: duplicate content, identity leakage and distribution summaries."""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from .dataset import DatasetEntry
from .features import extract_features
import hashlib

@dataclass(frozen=True)
class QualityReport:
    count: int
    duplicate_sequence_groups: list[list[str]]
    cross_split_leaks: list[list[str]]
    conflicting_labels: list[list[str]]
    split_counts: dict[str, int]
    label_counts: dict[str, int]
    mean_length: float | None
    mean_entropy: float | None

def audit_dataset(entries: list[DatasetEntry]) -> QualityReport:
    hashes: dict[str, list[DatasetEntry]] = defaultdict(list)
    for e in entries:
        hashes[hashlib.sha256(e.sequence.encode()).hexdigest()].append(e)
    groups = [v for v in hashes.values() if len(v) > 1]
    return QualityReport(
        count=len(entries),
        duplicate_sequence_groups=[sorted(e.identifier for e in v) for v in groups],
        cross_split_leaks=[sorted(e.identifier for e in v) for v in groups if len({e.split for e in v}) > 1],
        conflicting_labels=[sorted(e.identifier for e in v) for v in groups if len({e.label for e in v}) > 1],
        split_counts=dict(sorted(Counter(e.split for e in entries).items())),
        label_counts=dict(sorted(Counter(e.label for e in entries).items())),
        mean_length=(sum(len(e.sequence) for e in entries)/len(entries)) if entries else None,
        mean_entropy=(sum(extract_features(e.sequence).entropy_bits for e in entries)/len(entries)) if entries else None,
    )

def audit_dict(entries: list[DatasetEntry]) -> dict[str, object]:
    return asdict(audit_dataset(entries))
