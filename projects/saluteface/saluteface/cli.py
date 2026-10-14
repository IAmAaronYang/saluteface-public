"""Command line interface for experimental research workflows."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from .fasta import read_fasta
from .dataset import build_entries, serialize_jsonl, manifest, parse_jsonl
from .watermark import WatermarkCodec
from .evaluate import evaluate


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="saluteface", description="Reproducible protein sequence research tools")
    subs = p.add_subparsers(dest="command", required=True)
    convert = subs.add_parser("convert", help="Convert FASTA to deterministic JSONL and manifest")
    convert.add_argument("input", type=Path)
    convert.add_argument("output", type=Path)
    convert.add_argument("--source", required=True)
    verify = subs.add_parser("verify", help="Evaluate toy keyed watermark agreement")
    verify.add_argument("input", type=Path)
    verify.add_argument("--key-env", default="SALUTEFACE_EXPERIMENT_KEY")
    scan = subs.add_parser("validate", help="Validate dataset JSONL")
    scan.add_argument("input", type=Path)
    qc = subs.add_parser("audit", help="Check JSONL dataset for duplicate and cross-split leakage")
    qc.add_argument("input", type=Path)
    qc.add_argument("--output", type=Path)
    feat = subs.add_parser("features", help="Export sequence feature records from FASTA")
    feat.add_argument("input", type=Path)
    feat.add_argument("output", type=Path)
    bench = subs.add_parser("benchmark", help="Run synthetic watermark robustness benchmark")
    bench.add_argument("input", type=Path)
    bench.add_argument("output", type=Path)
    bench.add_argument("--key-env", default="SALUTEFACE_EXPERIMENT_KEY")
    bench.add_argument("--seed", type=int, default=42)
    bench.add_argument("--edits", type=int, default=1)
    sim = subs.add_parser("similarity", help="Identify near-duplicate protein sequences")
    sim.add_argument("input", type=Path)
    sim.add_argument("--threshold", type=float, default=.8)
    sim.add_argument("--k", type=int, default=3)
    align = subs.add_parser("align", help="Globally align two protein sequences")
    align.add_argument("left")
    align.add_argument("right")
    pipe = subs.add_parser("pipeline", help="Run FASTA to audited reproducible dataset and HF export")
    pipe.add_argument("input", type=Path)
    pipe.add_argument("output", type=Path)
    pipe.add_argument("--source", default="local-fasta")
    pipe.add_argument("--seed", default="saluteface-v3")
    ex = subs.add_parser("experiment", help="Comparative multi-budget watermark stress tests")
    ex.add_argument("input", type=Path)
    ex.add_argument("output", type=Path)
    ex.add_argument("--key-env", default="SALUTEFACE_EXPERIMENT_KEY")
    ex.add_argument("--seed", type=int, default=42)
    subs.add_parser("version", help="Print the package version")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "similarity":
        from dataclasses import asdict
        from .similarity import detect_near_duplicates, cluster_records
        records=list(read_fasta(args.input.read_text(encoding="utf-8").splitlines()))
        pairs=detect_near_duplicates(records,threshold=args.threshold,k=args.k)
        print(json.dumps({"pairs":[asdict(p) for p in pairs],"clusters":cluster_records(records,threshold=args.threshold,k=args.k)},indent=2))
        return 0
    if args.command == "align":
        from dataclasses import asdict
        from .alignment import align_global
        print(json.dumps(asdict(align_global(args.left,args.right)),indent=2))
        return 0
    if args.command == "pipeline":
        from .pipeline import run_pipeline,PipelineConfig
        result=run_pipeline(args.input,args.output,PipelineConfig(seed=args.seed,source=args.source))
        print(json.dumps(result,indent=2))
        return 0
    if args.command == "experiment":
        from .experiment import run_experiment
        from .report import export_report
        from .io_utils import atomic_json_write
        key=os.getenv(args.key_env)
        if not key:parser().error(f"set {args.key_env} in environment")
        sequences=[r.sequence for r in read_fasta(args.input.read_text(encoding="utf-8").splitlines())]
        result=run_experiment(sequences,key=key.encode(),seed=args.seed)
        atomic_json_write(args.output,result)
        export_report(result,args.output.with_suffix(".md"))
        print(f"wrote {len(result['trials'])} trials")
        return 0
    if args.command == "version":
        from . import __version__
        print(__version__)
        return 0
    if args.command == "convert":
        entries = build_entries(read_fasta(args.input.read_text(encoding="utf-8").splitlines()), source=args.source)
        output = serialize_jsonl(entries)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        args.output.with_suffix(args.output.suffix + ".manifest.json").write_text(json.dumps(manifest(entries, output.encode()), indent=2) + "\n", encoding="utf-8")
        print(f"wrote {len(entries)} entries")
        return 0
    if args.command == "validate":
        entries = parse_jsonl(args.input.read_text(encoding="utf-8"))
        print(json.dumps({"valid": True, "count": len(entries)}))
        return 0
    if args.command == "audit":
        from .quality import audit_dict
        from .io_utils import atomic_json_write
        result = audit_dict(parse_jsonl(args.input.read_text(encoding="utf-8")))
        if args.output:
            atomic_json_write(args.output, result)
        print(json.dumps(result, indent=2))
        return 1 if result["cross_split_leaks"] or result["conflicting_labels"] else 0
    if args.command == "features":
        from .features import feature_dict
        records = list(read_fasta(args.input.read_text(encoding="utf-8").splitlines()))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps({"identifier": record.identifier, **feature_dict(record.sequence)}, sort_keys=True) + "\n")
        print(f"wrote {len(records)} feature records")
        return 0
    if args.command == "benchmark":
        from .benchmark import run_benchmark, benchmark_dict
        from .io_utils import atomic_json_write
        key = os.getenv(args.key_env)
        if not key:
            parser().error(f"set {args.key_env} in environment")
        records = list(read_fasta(args.input.read_text(encoding="utf-8").splitlines()))
        report = benchmark_dict(run_benchmark(records, WatermarkCodec(key.encode()), edits=args.edits, seed=args.seed))
        atomic_json_write(args.output, report)
        print(f"wrote benchmark of {len(records)} sequences")
        return 0
    if args.command == "verify":
        raw = os.getenv(args.key_env)
        if not raw:
            parser().error(f"set {args.key_env} in the environment (never commit secrets)")
        codec = WatermarkCodec(raw.encode())
        outcome = [codec.verify(row.sequence).detected for row in read_fasta(args.input.read_text(encoding="utf-8").splitlines())]
        print(json.dumps({"evaluated": len(outcome), "detected": sum(outcome), "protocol": "educational-toy-not-SynthID"}))
        return 0
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
