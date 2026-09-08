VENV := .venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

.PHONY: run skip-ai clean

$(PYTHON):
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

run: $(PYTHON)
	$(PYTHON) main.py

skip-ai: $(PYTHON)
	$(PYTHON) main.py --skip-ai

clean:
	rm -rf output *.parquet
