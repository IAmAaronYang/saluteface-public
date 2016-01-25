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
