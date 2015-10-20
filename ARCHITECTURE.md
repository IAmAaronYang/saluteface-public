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
