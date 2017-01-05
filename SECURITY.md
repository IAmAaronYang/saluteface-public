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

