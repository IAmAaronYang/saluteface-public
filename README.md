# SchemaPilot

[![ci](https://github.com/bramrahanddian/SchemaPilot/actions/workflows/ci.yml/badge.svg)](https://github.com/bramrahanddian/SchemaPilot/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![python: 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

SchemaPilot is a deterministic structured output contract fuzzer. Point it at a
compact JSON contract and it will:

- **fuzz** the contract into reproducible valid and adversarial payloads,
- **validate** real payloads and report every violation with a stable code,
