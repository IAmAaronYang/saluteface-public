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

