# Research methods, v0.3

This repository adds *reproducible software experiments* and does not claim to reproduce SynthID Bio or prove protein watermark robustness in laboratory settings.

## Similarity and leakage

`similarity` performs exhaustive exact k-mer Jaccard comparisons. `minhash_signature` provides a compact approximate representation; exhaustive matching remains quadratic in sequences and is intended for modest research datasets. `group_split` puts all sequence-similarity clusters in one split to reduce train/test leakage. Transitive linkage may create large clusters; inspect grouping before production ML training.

## Alignments

`align_global` implements Needleman-Wunsch with constant gap penalty and deterministic traceback. This is **not** a structure or functional similarity model. Time and memory are O(mn), with configurable maximum cells. `levenshtein` uses O(min(m,n)) memory.

## Physicochemical descriptors

Average residue masses, Kyte-Doolittle hydropathy and raw charge proxy offer descriptive summaries only; pH-dependent exact charge, biochemical functionality, secondary structure and toxicity are **not** inferred.

## Statistical experiments

Binary detection rates include Wilson 95% confidence intervals. Bootstrap means and permutation differences are seeded for reproducibility. ROC AUC uses pairwise rank statistics. Results on synthetic sequences are not independent replication and must not be described as claims of attribution or real-world scientific superiority.

## Local Hugging Face export

The pipeline creates `train.csv`, `validation.csv`, and `test.csv`, dataset card and SHA-256 manifest. Uploading to HF is intentionally outside the tool; publishing is a separate user-authorized action and requires rights to source data.

## Run

```bash
python -m pip install -e '.[dev]'
python -m saluteface similarity examples/example.fasta --threshold 0.7
python -m saluteface align ACDEFG ACDFG
python -m saluteface pipeline examples/example.fasta output/pipeline --source example
export SALUTEFACE_EXPERIMENT_KEY=local-example-key
python -m saluteface experiment examples/example.fasta output/stress.json
pytest -q
```
