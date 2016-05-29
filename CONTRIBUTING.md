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
