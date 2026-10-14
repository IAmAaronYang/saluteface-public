"""Reproducible toy watermark robustness benchmark. Never evidence of biological origin."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from .watermark import WatermarkCodec
from .mutations import perturb
from .evaluate import BinaryMetrics, evaluate
from .sequence import SequenceRecord

@dataclass(frozen=True)
class BenchmarkResult:
    protocol: str
    examples: int
    attacks: tuple[str, ...]
    edit_count: int
    seed: int
    metrics: BinaryMetrics
    rows: tuple[dict[str, object], ...]

def run_benchmark(records: list[SequenceRecord], codec: WatermarkCodec,
                  *, attacks: tuple[str,...] = ("substitution", "deletion", "insertion"),
                  edits: int = 1, seed: int = 42) -> BenchmarkResult:
    if not records:
        raise ValueError("benchmark requires records")
    if edits < 0:
        raise ValueError("edits must not be negative")
    rows: list[dict[str, object]] = []
    decisions: list[tuple[bool,bool]] = []
    for r in records:
        for label, value, attack in [(False, r.sequence, "control"), (True, codec.embed(r.sequence), "embedded")]:
            checked = codec.verify(value)
            rows.append({"id": r.identifier, "attack": attack, "expected": label,
                         "detected": checked.detected, "agreement": checked.agreement,
                         "positions": checked.positions})
            decisions.append((label, checked.detected))
        marked = codec.embed(r.sequence)
        for attack in attacks:
            changed = perturb(marked, attack, edits, seed=seed, identifier=r.identifier).result
            checked = codec.verify(changed)
            rows.append({"id": r.identifier, "attack": attack, "expected": True,
                         "detected": checked.detected, "agreement": checked.agreement,
                         "positions": checked.positions})
            decisions.append((True, checked.detected))
    return BenchmarkResult("educational-toy-not-SynthID", len(records), attacks, edits, seed,
                           evaluate(decisions), tuple(rows))

def benchmark_dict(result: BenchmarkResult) -> dict[str, object]:
    return asdict(result)
