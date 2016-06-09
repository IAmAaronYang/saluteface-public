# Contributing

Thank you for helping improve SchemaPilot. This guide covers how to set up a
development environment, the conventions the project follows, and what a
reviewable change looks like.

## Development environment

SchemaPilot is dependency-free at runtime. You need:

- Python 3.11 or newer for the `schemapilot` package.
- The .NET 9 SDK for the `runtime/SchemaPilot.Runtime` project.

No third-party Python packages are required to run or exercise the tool. Ruff
and mypy are optional developer conveniences configured in `pyproject.toml`.

## Common tasks

```bash
make compile   # byte-compile the Python package
make build     # build the .NET runtime in Release
make inspect    # inspect the default contract
make report    # emit a Markdown report
make matrix    # cross-validate the invoice contracts
make parity    # check Python/.NET fingerprint parity
```

## Conventions

- **Standard library only** in `schemapilot/`. If you reach for a third-party
  dependency, open an issue first — it is almost always avoidable.
- **Keep the two runtimes in lockstep.** Any change to the contract grammar,
  the validator rules, or the canonical fingerprint must land in both the
  Python package and the .NET runtime in the same change.
- **Determinism is a contract.** Generation must stay reproducible. Do not use
  the global `random` module, wall-clock time, or unordered iteration in code
  paths that affect generated output or fingerprints.
- **Stable violation codes.** Treat the violation codes in `validator.py` as a
