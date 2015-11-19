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
