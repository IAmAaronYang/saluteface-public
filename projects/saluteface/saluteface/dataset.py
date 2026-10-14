"""JSONL dataset records, deterministic splits, manifests and checksums."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json
from collections.abc import Iterable
from .sequence import SequenceRecord, validate_sequence
from .errors import InvalidDataset


@dataclass(frozen=True)
class DatasetEntry:
    identifier: str
    sequence: str
    split: str
    label: str
    source: str

    def __post_init__(self) -> None:
        if not self.identifier or not self.source:
            raise InvalidDataset("identifier and source required")
        if self.split not in {"train", "validation", "test"}:
            raise InvalidDataset("invalid split")
        if self.label not in {"original", "modified"}:
            raise InvalidDataset("invalid label")
        object.__setattr__(self, "sequence", validate_sequence(self.sequence))


def assign_split(identifier: str, *, seed: str = "saluteface-v1") -> str:
    value = int(hashlib.sha256(f"{seed}:{identifier}".encode()).hexdigest()[:12], 16) % 100
    return "train" if value < 80 else "validation" if value < 90 else "test"


def build_entries(records: Iterable[SequenceRecord], *, source: str, label: str = "original", seed: str = "saluteface-v1") -> list[DatasetEntry]:
    return [DatasetEntry(r.identifier, r.sequence, assign_split(r.identifier, seed=seed), label, source) for r in records]


def serialize_jsonl(entries: Iterable[DatasetEntry]) -> str:
    return "".join(json.dumps(asdict(e), sort_keys=True, separators=(",", ":")) + "\n" for e in entries)


def parse_jsonl(text: str) -> list[DatasetEntry]:
    entries: list[DatasetEntry] = []
    seen: set[str] = set()
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
            if not isinstance(raw, dict) or set(raw) != set(DatasetEntry.__dataclass_fields__):
                raise InvalidDataset("incorrect entry fields")
            record = DatasetEntry(**raw)
            if record.identifier in seen:
                raise InvalidDataset("duplicate identifier")
            seen.add(record.identifier)
            entries.append(record)
        except (TypeError, ValueError) as exc:
            raise InvalidDataset(f"invalid JSONL on line {i}: {exc}") from exc
    return entries


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest(entries: list[DatasetEntry], content: bytes) -> dict[str, object]:
    return {"format": "saluteface-jsonl-v1", "records": len(entries), "sha256": checksum(content), "splits": {split: sum(e.split == split for e in entries) for split in ("train", "validation", "test")}, "sources": sorted({e.source for e in entries})}
