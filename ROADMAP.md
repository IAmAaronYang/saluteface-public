# Roadmap

SchemaPilot's mission is to make structured-output contracts testable: generate
the payloads that expose a break before your users do, and prove whether a
contract change is safe to deploy. This roadmap tracks the milestones that
build toward that mission.

## Delivered milestones

- [x] **M1 — Contract core.** Compact JSON contract grammar, parser, and a
  validator with stable violation codes for types, bounds, enums, patterns,
  string lengths, array sizes, required fields, and unexpected fields.
- [x] **M2 — Deterministic fuzzing.** Reproducible valid and labelled
  adversarial payload generation seeded from the contract fingerprint, with a
  library of single-fault mutations for scoring detectors.
