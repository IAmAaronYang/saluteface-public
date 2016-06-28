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
  public API. Add new codes rather than repurposing existing ones.
- Match the existing code style: type hints on public functions, dataclasses
  for value objects, and docstrings that explain intent.

## Making a change

1. Discuss anything that alters the contract grammar or a fingerprint in an
   issue before implementing it.
2. Implement the change in both runtimes when it affects shared semantics.
3. Update `docs/`, `ARCHITECTURE.md`, and `CHANGELOG.md` as needed.
4. Verify locally:
   - `make compile` succeeds.
   - `make build` reports zero errors.
   - `make parity` shows matching fingerprints for every contract in
     `schemas/`.
   - Reports for the shipped contracts still reach full detection accuracy.
5. Open a pull request using the template and describe what you verified.

