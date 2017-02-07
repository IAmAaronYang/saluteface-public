"""SchemaPilot — Structured Output Contract Fuzzer.

SchemaPilot reads a compact JSON *contract*, deterministically synthesises
valid and adversarial payloads, validates payloads against the contract
(fields, types, bounds, enums, patterns), proposes minimal *repairs* for
invalid payloads, and publishes compatibility matrices and reports in JSON
and Markdown.

