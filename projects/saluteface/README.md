# Saluteface Research Toolkit

Reproducible open-source tools for protein-sequence dataset preparation, validation, lightweight provenance manifests, and **educational** watermark experiments.

> **Scope and provenance:** This repository is an original experimental implementation. It is **not** an official release by Orbofi, SalutefaceAAC, Hugging Face, Google DeepMind or SynthID Bio, and it does not assert that an autonomous agent authored any third-party research. The watermark algorithm is an intentionally simple illustrative protocol, **not** an implementation of SynthID Bio, and must not be used to claim biological fidelity or provenance.

## Features

- Strict amino-acid sequence validation and streaming FASTA parsing.
- Deterministic 80/10/10 train/validation/test assignment.
- Strict JSONL contracts; reproducible SHA-256 dataset manifests.
- Deterministic keyed educational watermark substitution experiment.
- True/false positive detection metrics and explicit undefined denominator handling.
- Local provenance records with honest self-attestation scope.
- CLI and unit tests across supported Python versions.
- Dependency-light standard-library implementation.

## Install & run

```bash
python -m venv .venv
source .venv/bin/activate   # Windows Git Bash: source .venv/Scripts/activate
python -m pip install -e '.[dev]'
pytest -q
saluteface convert examples/example.fasta output/dataset.jsonl --source synthetic-example
saluteface validate output/dataset.jsonl
SALUTEFACE_EXPERIMENT_KEY=local-test-key saluteface verify examples/example.fasta
```

## Scientific limitations

- The watermark substitutions modify protein primary sequences; no claim of retained biological function.
- Detection scores are experimental and not validated on real biological datasets.
- Data in `examples/` is synthetic illustrative data, not scraped or copied from other projects.
- Reproducibility and provenance hashes are not proofs of research authorship or on-chain publication.

## Integration with SchemaPilot

The supplied ZIP is a **self-contained overlay**, not a copy of SchemaPilot or its history. Clone SchemaPilot and copy the overlay on top. Before doing so, check its MIT license and choose whether to preserve SchemaPilot's own project identity and docs separately. A sensible integration is to move SchemaPilot's existing code into an `integrations/schemapilot/` adapter in a future PR rather than presenting unrelated prior commits as Saluteface development history. The repository should retain original author attribution and history; never rewrite or backdate contributions to claim artificial project age.

## Related public research (not incorporated here)

- https://huggingface.co/datasets/SalutefaceAAC/synthidbio-sequence-pilot/discussions/1
- https://www.orbofi.com/agent/salute-face
- https://www.orbofi.com/aac/4663/0xA583222dD1Af98820DA4234a6fE14c91E4465AAC

These are links for context only and do not establish endorsement, ownership or integration.

## License

MIT for this new code. Third-party code retains its original license and attribution.

## Expanded research modules

- `saluteface.features`: residue entropy, k-mer statistics and compositional profiles.
- `saluteface.mutations`: reproducible insertions, deletions and substitutions.
- `saluteface.quality`: duplicate detection, split leakage and conflicting-label audits.
- `saluteface.benchmark`: control/embedding/attack benchmark with actual detector outcomes.
- `saluteface.io_utils`: atomic JSON report writing.

See [BENCHMARKS.md](docs/BENCHMARKS.md) for executable commands.

## Version 0.3 — executable research pipeline

Added seven research modules: `similarity`, `alignment`, `structure`, `significance`, `splits`, `hub_export`, `pipeline`, `experiment`, `report`, and more than twenty new unit/integration tests. The workflows perform real computations rather than precomputed output. See [Methods and limitations](docs/V3_METHODS.md).

```bash
python -m pip install -e '.[dev]'
python -m saluteface pipeline examples/example.fasta ./output/pipeline
SALUTEFACE_EXPERIMENT_KEY=local-key python -m saluteface experiment examples/example.fasta ./output/experiment.json
```

**Provenance:** Independent educational implementation; not the original Orbofi agent, not an official DeepMind/Hugging Face system, and no false claim of an autonomous research publication.
