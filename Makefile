# SchemaPilot developer tasks. Dependency-free by design: the Python package
# uses only the standard library, and the .NET runtime builds with the SDK.

PY ?= python
DOTNET ?= dotnet
CONTRACT ?= schemas/invoice.v1.json
RUNTIME := runtime/SchemaPilot.Runtime.csproj

.PHONY: help
help:
	@echo "SchemaPilot targets:"
	@echo "  make compile        Byte-compile the Python package"
	@echo "  make build          Build the .NET runtime in Release"
	@echo "  make inspect        Inspect the default contract (Python)"
	@echo "  make report         Emit a Markdown report for the default contract"
	@echo "  make matrix         Cross-validate the invoice contracts"
	@echo "  make parity         Check Python/.NET fingerprint parity"
