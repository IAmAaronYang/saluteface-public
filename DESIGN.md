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

