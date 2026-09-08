VENV := .venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

.PHONY: run skip-ai clean

$(PYTHON):
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

.env: .env.example
	cp .env.example .env

run: $(PYTHON) .env
	$(PYTHON) main.py

skip-ai: $(PYTHON) .env
	$(PYTHON) main.py --skip-ai

clean:
	rm -rf output *.parquet
