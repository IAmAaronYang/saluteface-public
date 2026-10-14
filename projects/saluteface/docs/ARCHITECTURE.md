# Architecture

`sequence` validates standard amino-acid records. `fasta` is the transport parser; it yields immutable records. `dataset` defines the JSONL contract, stable split assignment and content digest. `watermark` demonstrates deterministic keyed substitution and a score; the algorithm is intentionally not compatible with SynthID Bio. `evaluate` computes honest confusion-matrix metrics with undefined values represented as null. `provenance` constructs self-declared local lineage statements. `cli` wires these pure parts into filesystem commands.

## Security boundaries

- Secrets are provided through environment variables; they are never included in outputs or committed.
- Inputs are strictly validated, including maximum length for individual sequences.
- Large ingestion should use a streaming JSONL serializer for production.
- No automatic publishing to Hugging Face, GitHub or blockchains.
- No import-time network access and no dynamic execution of user-provided code.

## Roadmap

Integrate JSON Schema checks where SchemaPilot is suitable; add dataset cards, license validation, streaming exports, provenance signature verification and biological evaluation once ground-truth benchmarks are independently available.
