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

