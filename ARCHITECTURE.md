# Architecture

SchemaPilot is organised as a small pipeline of pure components. Every stage
consumes and produces plain data structures, so stages compose freely and each
one is independently testable. The Python package is the reference
implementation; the .NET runtime re-implements the parser, validator, and
fingerprint so the same contracts can be enforced inside a .NET service.

```
              +-------------+
  contract -->|   Contract  |-- fingerprint --> stable digest
   (JSON)     |   parser    |
              +------+------+
                     |
        +------------+------------+
        |            |            |
        v            v            v
   +---------+  +-----------+  +-----------+
   | Fuzzer  |  | Validator |  |  Repair   |
   +----+----+  +-----+-----+  +-----+-----+
        |             |              |
        |   payloads  |  violations  |  edits + repaired payload
        +------+------+------+-------+
               |             |
               v             v
          +---------+   +-----------+
          | Report  |   | Matrix    |
          +---------+   +-----------+
           JSON / MD     verdicts
```

## Modules

### `schemapilot.contract`

Parses a compact JSON contract into a `Contract` of named `FieldSpec` entries.
The parser performs structural sanity checks (`min <= max`, valid regex,
consistent `items`) and rejects unknown field types. `Contract.fingerprint()`
serialises the normalised contract to canonical JSON (keys sorted, no
whitespace), SHA-256s it, and returns the first 16 hex characters. The
fingerprint is the project's identity primitive: it seeds deterministic
generation and detects contract drift.

### `schemapilot.fuzzer`

Turns a contract into a deterministic stream of `FuzzCase` objects. A tiny
linear-congruential generator seeded from the contract fingerprint XOR the user
seed drives all randomness, so the same inputs always produce the same cases
without touching the global `random` state. Two families are produced: `valid`
payloads that satisfy every constraint, and `adversarial` payloads that violate
exactly one constraint in a labelled way, giving detectors a ground truth.

### `schemapilot.validator`

Checks a payload against a contract and returns a `ValidationResult` of
`Violation` records. Each violation carries a stable machine code, the field
path, a human message, and the observed/expected values. The type checks are
strict: booleans are rejected for integer and number fields because `bool` is a
subclass of `int` in Python, and patterns use anchored full-match semantics.

### `schemapilot.repair`

Given a contract and an invalid payload, computes the smallest set of `Edit`
operations that make the payload conform: insert defaults, drop unexpected
fields, coerce types, snap enums, clamp bounds, pad/truncate strings and
arrays. It re-validates after each pass (bounded by `max_passes`) and reports
whether the payload is now conforming. Each pass recomputes violations from the
current payload, so edits that resolve one violation can never hide another.

### `schemapilot.matrix`

Cross-validates the valid payloads generated for each contract against every
other contract and summarises pass rates into a matrix of `Cell` objects. Each
contract pair receives a verdict — `identical`, `forward`, `backward`, `full`,
or `breaking` — that answers "will deploying this contract change break my
producers or consumers?".

### `schemapilot.report`

Builds a `RunReport` from a fuzz-and-validate pass, scoring whether each case
behaved as expected (valid cases pass, adversarial cases fail). It emits JSON
for machines and Markdown for humans from the same in-memory model.

### `schemapilot.cli`

A thin argparse front end wiring the modules into the `inspect`, `fuzz`,
`validate`, `repair`, `report`, and `matrix` commands. It reads and writes JSON
and returns distinct exit codes per failure class for CI gating: 0 success,
1 validation findings, 2 unrepaired payload, 3 contract error, 4 missing file,
5 invalid JSON. The codes are stable and safe to branch on.

## .NET runtime (`runtime/`)

`Contract.cs`, `Validator.cs`, and `Fingerprinter.cs` mirror the Python
semantics. `Fingerprinter.cs` reconstructs the exact canonical JSON that the
Python `Contract.to_dict()` produces — including `enum`, `items`, and `default`
members, sorted keys, and Python-compatible number rendering — so both runtimes
compute identical digests. `Program.cs` exposes `inspect`, `validate`, and
`fingerprint`.

## Determinism and parity

Two invariants hold the system together:

1. **Determinism.** Given the same contract and seed, generation is
   byte-for-byte reproducible across processes and platforms.
2. **Parity.** The Python and .NET validators accept exactly the same payloads,
   and both runtimes compute the same contract fingerprint.

These invariants are what make SchemaPilot's reports diffable in code review
and safe to gate a deployment on.
