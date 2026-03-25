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
git clone https://github.com/bramrahanddian/SchemaPilot
cd SchemaPilot

python -m schemapilot inspect schemas/invoice.v1.json
python -m schemapilot fuzz schemas/invoice.v1.json --seed 7 --valid 3 --adversarial 2
python -m schemapilot validate schemas/invoice.v1.json fixtures/invoice_invalid.json
python -m schemapilot repair schemas/invoice.v1.json fixtures/invoice_invalid.json
python -m schemapilot report schemas/invoice.v1.json --format markdown
python -m schemapilot matrix schemas/invoice.v1.json schemas/invoice.v2.json
```

`make demo` runs inspect, report, and matrix end to end on the shipped
contracts.

## Commands

| Command    | What it does                                                             |
|------------|--------------------------------------------------------------------------|
| `inspect`  | Parse a contract, print its normalised form and fingerprint.             |
| `fuzz`     | Generate deterministic valid and adversarial payloads.                   |
| `validate` | Validate a payload file against a contract.                              |
| `repair`   | Compute a minimal repair plan for an invalid payload.                    |
| `report`   | Run a full fuzz+validate pass; emit JSON or Markdown.                    |
| `matrix`   | Cross-validate contracts and print compatibility verdicts.               |

Exit codes are stable for CI gating: `0` success, `1` validation findings,
`2` unrepaired payload, `3` contract error, `4` missing file, `5` invalid JSON.

## Contracts

A contract is a small, diffable JSON document: a flat `fields` map with a
fixed set of constraints (`type`, `required`, `nullable`, `enum`, `min`/`max`,
`min_len`/`max_len`, `pattern`, `min_items`/`max_items`, `items`, `default`).

```json
{
  "name": "invoice",
  "version": 1,
  "fields": {
    "id":       { "type": "string",  "pattern": "^INV-[0-9]{6}$", "required": true },
    "total":    { "type": "number",  "min": 0, "required": true },
    "currency": { "type": "string",  "enum": ["USD", "EUR", "GBP"], "required": true },
    "paid":     { "type": "boolean", "default": false }
  }
}
```

The fingerprint of the normalised contract is its identity primitive: it seeds
deterministic generation and flags contract drift between revisions.

## .NET runtime

`runtime/SchemaPilot.Runtime` re-implements the parser, validator, and
fingerprint for .NET services:

```bash
dotnet run -c Release --project runtime/SchemaPilot.Runtime.csproj -- fingerprint schemas/invoice.v1.json
```

Both runtimes must compute the same digest; CI verifies cross-runtime parity for
every contract in `schemas/`.

## Repository layout

```
schemapilot/    Python package: contract, fuzzer, validator, repair, matrix, report, cli
runtime/        .NET 9 runtime mirroring the parser, validator, and fingerprint
schemas/        Example contracts (invoice v1/v2, telemetry event v1)
fixtures/       Valid and invalid payload examples used by the docs and CI
docs/assets/    Diagrams referenced by the documentation
```

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - modules and data flow.
- [DESIGN.md](DESIGN.md) - the decisions behind the contract vocabulary.
- [ROADMAP.md](ROADMAP.md) - delivered and planned milestones.
- [CHANGELOG.md](CHANGELOG.md) - release history.

## Contributing

Issues and pull requests are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md)
first; it explains how to keep the two runtimes in lockstep and why determinism
is treated as a contract. Security reports follow [SECURITY.md](SECURITY.md).
Participation is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md).

## License

MIT. See [LICENSE](LICENSE).

<!-- draft note 1333 -->
