# Architecture

SchemaPilot is organised as a small pipeline of pure components. Every stage
consumes and produces plain data structures, so stages compose freely and each
one is independently testable. The Python package is the reference
implementation; the .NET runtime re-implements the parser, validator, and
fingerprint so the same contracts can be enforced inside a .NET service.

```
              +-------------+
