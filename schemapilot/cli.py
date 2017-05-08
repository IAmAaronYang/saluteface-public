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
from typing import List, Optional

from schemapilot.contract import load_contract, ContractError
from schemapilot.fuzzer import Fuzzer
from schemapilot.matrix import CompatibilityMatrix
from schemapilot.repair import repair_payload
from schemapilot.report import run_report, to_json, to_markdown
from schemapilot.validator import Validator


def _read_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cmd_inspect(args: argparse.Namespace) -> int:
    contract = load_contract(Path(args.contract))
    out = contract.to_dict()
    out["fingerprint"] = contract.fingerprint()
    print(json.dumps(out, indent=2))
    return 0


def _cmd_fuzz(args: argparse.Namespace) -> int:
    contract = load_contract(Path(args.contract))
    fuzzer = Fuzzer(contract, seed=args.seed)
    cases = fuzzer.all_cases(valid_count=args.valid, adversarial_per_field=args.adversarial)
    print(json.dumps([c.to_dict() for c in cases], indent=2))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    contract = load_contract(Path(args.contract))
    payload = _read_json(args.payload)
    result = Validator(contract, allow_extra=args.allow_extra).validate(payload)
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.ok else 1


def _cmd_repair(args: argparse.Namespace) -> int:
    contract = load_contract(Path(args.contract))
    payload = _read_json(args.payload)
    plan = repair_payload(contract, payload)
    print(json.dumps(plan.to_dict(), indent=2))
    return 0 if plan.repaired_ok else 2


def _cmd_report(args: argparse.Namespace) -> int:
    contract = load_contract(Path(args.contract))
    report = run_report(
        contract,
        seed=args.seed,
        valid_count=args.valid,
        adversarial_per_field=args.adversarial,
    )
    if args.format == "markdown":
        print(to_markdown(report))
    else:
        print(to_json(report))
