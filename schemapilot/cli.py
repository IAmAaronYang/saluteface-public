"""SchemaPilot command-line interface.

Usage::

    python -m schemapilot <command> [options]

Commands
--------
``inspect``   Parse a contract and print its normalised form + fingerprint.
``fuzz``      Generate deterministic valid/adversarial payloads.
``validate``  Validate a payload file against a contract.
``repair``    Compute a minimal repair plan for a payload.
``report``    Run a full fuzz+validate pass and emit JSON or Markdown.
``matrix``    Build a compatibility matrix across multiple contracts.

All commands read/write JSON and never touch the network.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
