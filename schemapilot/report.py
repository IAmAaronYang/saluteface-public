"""Report emitters.

SchemaPilot produces two report formats from a fuzz+validate run:

- **JSON** — a machine-readable envelope for CI gates and dashboards.
- **Markdown** — a human-readable summary with tables, suitable for PR
  comments and release notes.

Both formats are derived from the same in-memory :class:`RunReport` so the
two never drift.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List

from schemapilot.contract import Contract
from schemapilot.fuzzer import Fuzzer, FuzzCase
from schemapilot.validator import Validator


@dataclass
class CaseOutcome:
    case: FuzzCase
    ok: bool
    codes: List[str]
    expected_fault: bool  # True for adversarial cases (should fail)

    @property
    def correct(self) -> bool:
        # Valid cases should pass; adversarial cases should fail.
        return self.ok != self.expected_fault

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case.case_id,
            "kind": self.case.kind,
            "mutation": self.case.mutation,
            "target_field": self.case.target_field,
            "ok": self.ok,
            "codes": self.codes,
            "correct": self.correct,
        }


@dataclass
class RunReport:
    contract: Contract
    outcomes: List[CaseOutcome] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.outcomes)

    @property
    def correct(self) -> int:
        return sum(1 for o in self.outcomes if o.correct)

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0
