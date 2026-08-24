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
	@echo "  make demo           Run inspect + report + matrix end-to-end"
	@echo "  make clean          Remove build artefacts and caches"

.PHONY: compile
compile:
	$(PY) -m compileall -q schemapilot

.PHONY: build
build:
	$(DOTNET) build -c Release $(RUNTIME)

.PHONY: inspect
inspect:
	$(PY) -m schemapilot inspect $(CONTRACT)

.PHONY: report
report:
	$(PY) -m schemapilot report $(CONTRACT) --format markdown

.PHONY: matrix
matrix:
	$(PY) -m schemapilot matrix schemas/invoice.v1.json schemas/invoice.v2.json

.PHONY: parity
parity: build
	$(PY) -m schemapilot inspect $(CONTRACT) | $(PY) -c "import sys,json;print('py',json.load(sys.stdin)['fingerprint'])"
	$(DOTNET) run -c Release --project $(RUNTIME) -- fingerprint $(CONTRACT)

.PHONY: demo
demo: inspect report matrix

.PHONY: clean
clean:
	$(PY) -c "import shutil,glob,os;[shutil.rmtree(p,ignore_errors=True) for p in glob.glob('**/__pycache__',recursive=True)]"
	$(PY) -c "import shutil;shutil.rmtree('runtime/bin',ignore_errors=True);shutil.rmtree('runtime/obj',ignore_errors=True)"
