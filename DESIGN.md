# Design

This document records the design decisions behind SchemaPilot and the
trade-offs each one implies. It complements `ARCHITECTURE.md`, which describes
*what* the components are; this document explains *why* they are shaped that
way.

## Goals

- **Deterministic by construction.** The same contract and seed must always
  produce the same payloads and reports, so results are diffable and CI is
  reproducible.
- **Dependency-free.** The Python package uses only the standard library and
  the .NET runtime uses only the base SDK, so SchemaPilot runs in air-gapped
  environments without a package resolution step.
- **Two-runtime parity.** A contract validated in Python and in .NET must
  reach identical conclusions, because contracts are enforced at the producer
  (often Python tooling) and the consumer (often a .NET service).
- **Auditable transformations.** Every repair is an explicit edit record so a
  reviewer can see exactly how a payload was changed.

## Non-goals

- SchemaPilot is not a general JSON Schema implementation. The contract
  vocabulary is deliberately small and opinionated to stay diffable.
- SchemaPilot does not attempt to *prove* two contracts are equivalent; the
  compatibility matrix reports empirical pass rates over generated payloads.
- SchemaPilot does not perform network I/O.

## Key decisions

### A compact contract vocabulary

JSON Schema is expressive but verbose and hard to review. SchemaPilot uses a
flat `fields` map with a fixed set of constraints (`type`, `required`,
`nullable`, `enum`, `min`/`max`, `min_len`/`max_len`, `pattern`,
`min_items`/`max_items`, `items`, `default`). This keeps a contract legible in
a pull request and keeps the validator and fuzzer small enough to re-implement
faithfully in a second language.

### Fingerprint as identity

Rather than compare contracts field by field, SchemaPilot canonicalises a
contract to sorted, whitespace-free JSON and hashes it. The 16-hex-character
digest is short enough to embed in report headers and stable enough to seed the
fuzzer. Because generation is seeded from the fingerprint, two byte-identical
contracts produce byte-identical payloads.
