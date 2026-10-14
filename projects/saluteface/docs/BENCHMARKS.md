# Reproducible synthetic benchmarks

The included watermark is an **original teaching protocol**, not SynthID Bio. Substituting residues can alter protein function. Do not use generated sequences as biological evidence, measured performance, or validation of model provenance.

## Run the full local evaluation

```bash
export SALUTEFACE_EXPERIMENT_KEY=local-demo-test-key
saluteface features examples/example.fasta output/features.jsonl
saluteface convert examples/example.fasta output/dataset.jsonl --source local-example
saluteface audit output/dataset.jsonl --output output/audit.json
saluteface benchmark examples/example.fasta output/benchmark.json --edits 1 --seed 42
```

The evaluation records explicit controls, embedded sequences, and insertion/deletion/substitution attacks. Reports contain reproducible outcomes and confusion-matrix statistics, not pre-scripted success claims. More robust protocols require sequence-function evaluation and independent datasets.
