# SchemaPilot developer tasks. Dependency-free by design: the Python package
# uses only the standard library, and the .NET runtime builds with the SDK.

PY ?= python
DOTNET ?= dotnet
CONTRACT ?= schemas/invoice.v1.json
RUNTIME := runtime/SchemaPilot.Runtime.csproj

.PHONY: help
help:
	@echo "SchemaPilot targets:"
