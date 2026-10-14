"""Streaming FASTA reader/writer with explicit duplicate handling."""
from __future__ import annotations
from collections.abc import Iterable, Iterator
from .sequence import SequenceRecord
from .errors import InvalidDataset


def read_fasta(lines: Iterable[str], *, allow_duplicates: bool = False) -> Iterator[SequenceRecord]:
    header: str | None = None
    sequence: list[str] = []
    seen: set[str] = set()
    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith(">"):
            if header is not None:
                yield _finish(header, sequence, seen, allow_duplicates)
            header = line[1:].strip()
            if not header:
                raise InvalidDataset(f"empty FASTA header on line {number}")
            sequence = []
        else:
            if header is None:
                raise InvalidDataset(f"sequence before first header on line {number}")
            sequence.append(line)
    if header is not None:
        yield _finish(header, sequence, seen, allow_duplicates)


def _finish(header: str, sequence: list[str], seen: set[str], allow_duplicates: bool) -> SequenceRecord:
    identifier, _, description = header.partition(" ")
    if identifier in seen and not allow_duplicates:
        raise InvalidDataset(f"duplicate identifier: {identifier}")
    seen.add(identifier)
    return SequenceRecord(identifier, "".join(sequence), description)


def write_fasta(records: Iterable[SequenceRecord], *, width: int = 80) -> str:
    if width <= 0:
        raise ValueError("width must be positive")
    lines: list[str] = []
    for record in records:
        lines.append(">" + record.identifier + (" " + record.description if record.description else ""))
        lines.extend(record.sequence[i:i + width] for i in range(0, len(record.sequence), width))
    return "\n".join(lines) + ("\n" if lines else "")
