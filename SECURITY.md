# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |
| 0.x     | No        |

## Reporting a vulnerability

SchemaPilot parses local JSON files and never performs network I/O. It is not
expected to handle secrets: contracts and payloads are test data and should
not contain credentials.

If you find a security issue - for example a crash or unbounded resource use
on a hostile contract, a path handling problem in the CLI, or a report that
leaks file contents beyond the fields it flags - please report it privately
