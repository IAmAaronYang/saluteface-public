"""Contract compatibility matrix.

When a contract evolves (``invoice.v1`` -> ``invoice.v2``), you want to know
whether payloads produced for one version still satisfy the other. The
:class:`CompatibilityMatrix` cross-validates the *valid* fixtures generated
for each contract against every other contract and summarises the pass rate
into a matrix, along with a compatibility *verdict* per pair:

``identical``
    Same fingerprint.
``forward``
    New contract accepts old payloads (relaxed constraints / added optionals).
``backward``
    Old contract accepts new payloads.
``full``
    Both directions pass — safe to deploy in any order.
``breaking``
    Neither direction reaches the acceptance threshold.

The matrix is the backbone of SchemaPilot's "will this deploy break my
downstream consumers?" workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from schemapilot.contract import Contract
from schemapilot.fuzzer import Fuzzer
from schemapilot.validator import Validator


@dataclass
class Cell:
    producer: str
    consumer: str
    total: int
    passed: int

    @property
    def rate(self) -> float:
        return self.passed / self.total if self.total else 0.0

    def to_dict(self) -> Dict[str, object]:
        return {
            "producer": self.producer,
            "consumer": self.consumer,
            "total": self.total,
            "passed": self.passed,
            "rate": round(self.rate, 4),
        }


class CompatibilityMatrix:
    def __init__(self, contracts: List[Contract], *, threshold: float = 1.0, sample: int = 6) -> None:
        self.contracts = contracts
        self.threshold = threshold
        self.sample = sample
        self.cells: Dict[str, Cell] = {}

    def _label(self, c: Contract) -> str:
        return f"{c.name}@{c.version}"

    def build(self) -> "CompatibilityMatrix":
        # Generate a fixed pool of valid payloads per contract.
        pools = {}
        for c in self.contracts:
            fz = Fuzzer(c, seed=7)
            pools[self._label(c)] = [
                fc.payload for fc in fz.generate(valid_count=self.sample, adversarial_per_field=0)
            ]
        for producer in self.contracts:
            plabel = self._label(producer)
            for consumer in self.contracts:
                clabel = self._label(consumer)
                validator = Validator(consumer, allow_extra=True)
