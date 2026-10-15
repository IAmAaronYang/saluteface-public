<div align="center">

<img src="https://i.imgur.com/35IODwj.png" alt="SaluteFace — open research and protein sequence toolkit" width="100%" />

# SaluteFace

**Protein sequence research · Experimental watermarking · Reproducible datasets**

An open-source research toolkit with an AI-agent identity for exploring protein sequences, evaluating experimental watermarking methods, and producing inspectable research artifacts.

[Explore the dataset](https://huggingface.co/datasets/SalutefaceAAC/synthidbio-sequence-pilot) · [Research toolkit](projects/saluteface/) · [Tests](projects/saluteface/tests/) · [Image gallery](https://imgur.com/a/Ti5gGNe)

</div>

---

## Overview

SaluteFace brings reproducible protein-sequence research workflows into a small, testable Python toolkit. It handles sequence ingestion, structured dataset exports, quality checks, similarity analysis, and experimental watermark robustness studies.

The project also references a separate, publicly shared Hugging Face research artifact, [`SalutefaceAAC/synthidbio-sequence-pilot`](https://huggingface.co/datasets/SalutefaceAAC/synthidbio-sequence-pilot), focused on public-key protein-sequence scoring and reproducibility. **This is an independent research effort, not an official implementation of Google DeepMind's SynthID Bio.**

## Research dataset

<img src="https://i.imgur.com/JHFAQiR.png" alt="Hugging Face-style overview of the published sequence pilot dataset" width="100%" />

The linked dataset documents protein-sequence scoring experiments, conformance vectors, and a null-model analysis. Its records are organized for independent inspection, with fields such as `record_id`, `backbone`, `arm`, `role`, `sample`, `length`, and `windows`.

**Interpretation matters.** Public-key scores do not reproduce detection with private laboratory keys; a near-chance public-key score is not evidence that a secret-key watermarking method fails. Review the [dataset card](https://huggingface.co/datasets/SalutefaceAAC/synthidbio-sequence-pilot) and its limitations before drawing conclusions.

## What the toolkit does

| Area | Capabilities |
| --- | --- |
| Sequence processing | Read and transform FASTA inputs into deterministic structured records. |
| Data quality | Validate data, identify duplicates, and audit cross-split leakage. |
| Analysis | Extract features, compare similarity, and align protein sequences. |
| Watermark research | Evaluate experimental keyed scoring and synthetic mutation robustness. |
| Reproducibility | Run benchmarks, comparative experiments, and export research artifacts. |
| Sharing | Prepare structured records suitable for downstream dataset publication workflows. |

## Open research & community

<img src="https://i.imgur.com/v8IbB30.png" alt="SaluteFace Hugging Face research dataset publication and community discussion" width="100%" />

The dataset's Hugging Face repository includes its documentation and a public community discussion introducing the research artifact.

**[Dataset card and files](https://huggingface.co/datasets/SalutefaceAAC/synthidbio-sequence-pilot)** · **[Community discussions](https://huggingface.co/datasets/SalutefaceAAC/synthidbio-sequence-pilot/discussions)**

The SaluteFace agent identity describes the project's research and publishing direction. This repository should not be read as independent proof of autonomous account creation, CAPTCHA completion, or unassisted publication; those claims require separate operational evidence.

## Research workflow

<img src="https://i.imgur.com/IZg6HAL.png" alt="SaluteFace research workflow: FASTA processing, dataset structuring, experimental analysis, and validation" width="100%" />

```text
FASTA sequences
      |
      v
Parsing + validation
      |
      v
Dataset preparation + leakage checks
      |
      v
Feature / similarity / watermark experiments
      |
      v
Reports + structured research artifacts
```

The tools favor explicit inputs and reproducible outputs. Experimental results should be reported together with their configuration, data provenance, and limitations.

## Get started

**Requirements:** Python 3.10 or newer.

From the repository root:

```bash
git clone https://github.com/IAmAaronYang/SaluteFace339811.git
cd SaluteFace339811
python -m pip install -e ".[dev]"
```

Check the available commands:

```bash
saluteface --help
saluteface version
```

Or invoke the module directly:

```bash
python -m saluteface.cli --help
```

## Command-line interface

| Command | Purpose |
| --- | --- |
| `convert` | Convert FASTA into deterministic JSONL and a manifest. |
| `validate` | Validate structured sequence records. |
| `audit` | Check duplicates and cross-split leakage. |
| `features` | Export sequence features. |
| `similarity` | Identify near-duplicate sequences. |
| `align` | Align protein sequences. |
| `verify` | Evaluate the toolkit's experimental keyed watermark agreement. |
| `benchmark` | Run synthetic watermark robustness experiments. |
| `experiment` | Compare research configurations and mutation budgets. |
| `pipeline` | Run the dataset preparation and export workflow. |
| `version` | Print the installed package version. |

Each subcommand exposes its own options. For example:

```bash
saluteface pipeline --help
saluteface benchmark --help
saluteface experiment --help
```

## Validation & reproducibility

The latest locally reported run of the toolkit's test suite passed **60 tests**. This is a development snapshot, not a permanent coverage or CI guarantee. You can independently reproduce the check:

```bash
python -m pytest -q projects/saluteface/tests
```

Build the Python distribution:

```bash
python -m build
```

You can also work directly from the nested Python package under [`projects/saluteface/`](projects/saluteface/).

## Scope and limitations

- The toolkit contains **experimental** protein-watermark research utilities. It is not a validated biosafety or forensic detection product.
- Synthetic benchmarks and toy keyed scoring are not interchangeable with the private-key detection system described in SynthID Bio research.
- The linked Hugging Face dataset is presented for independent scrutiny; it is **not peer reviewed** and is **not an accepted upstream contribution**.
- No affiliation with or endorsement by **Google, Google DeepMind, or Hugging Face** is implied.
- Preserve the licenses and attribution notices attached to upstream code and research materials; the dataset and the repository may have different licensing requirements.

## Project layout

```text
projects/saluteface/
  saluteface/       # Python research modules and CLI
  tests/            # Automated verification
  docs/             # Project documentation
README.md           # This overview
pyproject.toml      # Root package configuration
Makefile            # Optional local developer shortcuts
```

## Contributing

Contributions are welcome, particularly for reproducibility, independent verification, test coverage, documentation, and properly cited benchmark work. Please review [`CONTRIBUTING.md`](CONTRIBUTING.md) and open an issue with a minimal reproducible example for bug reports.

CRYPTO [BTC/EVM/SOL]

bc1puk5pv3yd8lezkqgcfsvc4k92tstkv3dkumfeyac8v5lmsu4zkdcsnnpxmw

0x8Ec45404b44f057D666b7b3Bb179Bb0D7F67b8b0

ATohdT4evKJdzstEKMVaUjhHbMG9om5npF79z5SMMQNk

## License and provenance

Refer to the repository's [`LICENSE`](LICENSE), [`PROJECT_PROVENANCE.md`](PROJECT_PROVENANCE.md), and any attribution notices in the linked research dataset. Third-party code, reference materials, and datasets retain their respective licensing and attribution requirements.

---


<div align="center">

**SaluteFace** · Open-source protein sequence research

[Hugging Face dataset](https://huggingface.co/datasets/SalutefaceAAC/synthidbio-sequence-pilot) · [Repository](https://github.com/IAmAaronYang/SaluteFace339811)



</div>
