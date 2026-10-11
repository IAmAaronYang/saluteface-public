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
- [x] **M3 — Repair and reporting.** Minimal, auditable repair plans plus
  JSON and Markdown reports that quantify detection accuracy per contract.
- [x] **M4 — Cross-runtime parity.** A .NET 9 runtime whose validator and
  contract fingerprint agree byte-for-byte with the Python package, so a
  payload accepted by one runtime is accepted by the other.

## In progress

- [ ] **M5 — Nested object contracts.** First-class `object` fields with their
  own `fields` map and recursive validation, generation, and repair.
- [ ] **M6 — Richer pattern synthesis.** Built-in generators for UUID,
  RFC 3339 timestamps, and email-shaped strings so patterned fields fuzz
  without hand-written seeds.

## Under consideration

- [ ] **M7 — Matrix visualisation.** An HTML heat-map export of the
  compatibility matrix for release reviews. The first cut will render the
  existing `matrix` JSON, so no new data model is needed.
- [ ] **M8 — Streaming contracts.** Validation of newline-delimited payload
  streams for high-throughput pipelines.

Milestones move from *Under consideration* to *In progress* once a design is
agreed in `DESIGN.md`, and to *Delivered* once shipped and covered by the
examples in this repository.
