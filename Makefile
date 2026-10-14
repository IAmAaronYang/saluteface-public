PYTHON ?= python

.PHONY: help install test compile lint build demo

help:
	@echo "SaluteFace Research Toolkit"

install:
	$(PYTHON) -m pip install -e "./projects/saluteface[dev]"

test:
	$(PYTHON) -m pytest -q projects/saluteface/tests

compile:
	$(PYTHON) -m compileall -q projects/saluteface/saluteface

lint:
	$(PYTHON) -m ruff check projects/saluteface/saluteface

build:
	$(PYTHON) -m build projects/saluteface

demo:
	$(PYTHON) -m saluteface.cli --help
