# SchemaPilot

[![ci](https://github.com/bramrahanddian/SchemaPilot/actions/workflows/ci.yml/badge.svg)](https://github.com/bramrahanddian/SchemaPilot/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![python: 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

SchemaPilot is a deterministic structured output contract fuzzer. Point it at a
compact JSON contract and it will:

- **fuzz** the contract into reproducible valid and adversarial payloads,
- **validate** real payloads and report every violation with a stable code,
- **repair** invalid payloads with a minimal, auditable list of edits,
- **matrix** two contracts to decide whether a change is safe to deploy,
- **report** the whole pass as JSON for machines or Markdown for review.

Generation is seeded from a canonical contract fingerprint, so the same
contract and seed always produce byte-identical payloads and reports. The
package is dependency-free - Python standard library only - and a .NET 9
runtime mirrors the parser, validator, and fingerprint so Python producers and
.NET consumers reach the same verdicts.

![SchemaPilot pipeline](docs/assets/pipeline.svg)

## Quick start

Python 3.11 or newer. There is nothing to install; run the package in place:

```bash
