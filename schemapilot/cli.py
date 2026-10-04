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
import os
import sys
from pathlib import Path
from typing import List, Optional

from schemapilot import __version__
from schemapilot.contract import load_contract, ContractError
from schemapilot.fuzzer import Fuzzer
from schemapilot.matrix import CompatibilityMatrix
from schemapilot.repair import repair_payload
from schemapilot.report import run_report, to_json, to_markdown
from schemapilot.validator import Validator


def _read_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ[name])
    except (KeyError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ[name])
    except (KeyError, ValueError):
        return default


def _env_choice(name: str, default: str, choices: tuple) -> str:
    value = os.environ.get(name, default)
    return value if value in choices else default


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
    return 0


def _cmd_matrix(args: argparse.Namespace) -> int:
    contracts = [load_contract(Path(p)) for p in args.contracts]
    matrix = CompatibilityMatrix(contracts, threshold=args.threshold).build()
    print(json.dumps(matrix.to_dict(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="schemapilot", description="Structured Output Contract Fuzzer")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    pi = sub.add_parser("inspect", help="parse and normalise a contract")
    pi.add_argument("contract")
    pi.set_defaults(func=_cmd_inspect)

    pf = sub.add_parser("fuzz", help="generate deterministic payloads")
    pf.add_argument("contract")
    pf.add_argument("--seed", type=int, default=_env_int("SCHEMAPILOT_SEED", 0))
    pf.add_argument("--valid", type=int, default=_env_int("SCHEMAPILOT_VALID_COUNT", 3))
    pf.add_argument("--adversarial", type=int,
                    default=_env_int("SCHEMAPILOT_ADVERSARIAL_PER_FIELD", 2))
    pf.set_defaults(func=_cmd_fuzz)

    pv = sub.add_parser("validate", help="validate a payload against a contract")
    pv.add_argument("contract")
    pv.add_argument("payload")
    pv.add_argument("--allow-extra", action="store_true")
    pv.set_defaults(func=_cmd_validate)

    pr = sub.add_parser("repair", help="compute a minimal repair plan")
    pr.add_argument("contract")
    pr.add_argument("payload")
    pr.set_defaults(func=_cmd_repair)

    prep = sub.add_parser("report", help="fuzz + validate and emit a report")
    prep.add_argument("contract")
    prep.add_argument("--seed", type=int, default=_env_int("SCHEMAPILOT_SEED", 0))
    prep.add_argument("--valid", type=int, default=_env_int("SCHEMAPILOT_VALID_COUNT", 3))
    prep.add_argument("--adversarial", type=int,
                      default=_env_int("SCHEMAPILOT_ADVERSARIAL_PER_FIELD", 3))
    prep.add_argument("--format",
                      choices=["json", "markdown"],
                      default=_env_choice("SCHEMAPILOT_REPORT_FORMAT", "json", ("json", "markdown")))
    prep.set_defaults(func=_cmd_report)

    pm = sub.add_parser("matrix", help="cross-contract compatibility matrix")
    pm.add_argument("contracts", nargs="+")
    pm.add_argument("--threshold", type=float,
                    default=_env_float("SCHEMAPILOT_MATRIX_THRESHOLD", 1.0))
    pm.set_defaults(func=_cmd_matrix)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ContractError as exc:
        print(f"contract error: {exc}", file=sys.stderr)
        return 3
    except FileNotFoundError as exc:
        print(f"file not found: {exc}", file=sys.stderr)
        return 4
    except json.JSONDecodeError as exc:
        print(f"invalid JSON: {exc}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
