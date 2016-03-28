# Changelog

All notable changes to SchemaPilot are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Nested-object field grammar (`type: "object"` with a `fields` map).
- Additional pattern generators for UUID and RFC 3339 timestamps.

## [1.0.1] - 2026-06-23

### Added

- `.NET 9` runtime (`SchemaPilot.Runtime`) with `inspect`, `validate`, and
  `fingerprint` commands mirroring the Python semantics.
- Cross-runtime contract fingerprint that agrees byte-for-byte between the
  Python package and the .NET runtime.

### Fixed

- Deterministic generator now emits hex-conforming values for the
  `^[a-f0-9]{8}$` pattern, so generated "valid" payloads validate against
  their own contract and reports reach full detection accuracy.
- .NET fingerprint canonicalisation now includes `enum`, `items`, and
  `default` members, matching the Python canonical JSON exactly.

## [1.0.0] - 2024-12-03

### Added

- Stable 1.x CLI contract: `inspect`, `fuzz`, `validate`, `repair`, `report`,
  and `matrix` with documented exit codes for CI gating.
- Typed package marker (`py.typed`) and a documented public surface in
  `schemapilot.__all__`.

### Changed

- Python 3.11 is the minimum supported interpreter; the package remains
  dependency-free.

## [0.9.0] - 2023-11-14

### Added

- Compatibility matrix (`schemapilot matrix`) with per-pair verdicts
  (`identical`, `forward`, `backward`, `full`, `breaking`).
- Architecture and design documents describing the pipeline and the
  trade-offs behind the compact contract vocabulary.
- Makefile tasks (`compile`, `build`, `inspect`, `report`, `matrix`, `parity`,
  `demo`).

## [0.7.0] - 2021-10-19

### Added

- JSON and Markdown report emitters (`schemapilot report`) sharing a single
  in-memory `RunReport` so the two never drift.
- Detection accuracy scoring: valid cases must pass and adversarial cases must
  fail for a pass to count as detected.

## [0.6.0] - 2020-11-10

### Added

- Minimal repair engine (`schemapilot repair`) producing an ordered, auditable
  list of edits and a re-validated payload.
- Repair strategies for missing-required, unexpected-field, null-not-allowed,
  type-mismatch, enum, bounds, string length, and array length violations.

## [0.5.0] - 2019-09-24

### Added

