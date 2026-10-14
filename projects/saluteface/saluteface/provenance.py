"""Local provenance attestations; cryptographic digests are not authorship proof."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json


@dataclass(frozen=True)
class Provenance:
    artifact_sha256: str
    created_at: str
    tool: str
    input_sha256: str | None
    declaration: str


def create_provenance(artifact: bytes, *, tool: str, input_data: bytes | None = None) -> Provenance:
    return Provenance(hashlib.sha256(artifact).hexdigest(), datetime.now(timezone.utc).isoformat(), tool, hashlib.sha256(input_data).hexdigest() if input_data is not None else None, "Self-reported computational lineage; independently verify source and authorship")


def to_json(provenance: Provenance) -> str:
    return json.dumps(asdict(provenance), indent=2, sort_keys=True) + "\n"
