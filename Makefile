PYTHON ?= python3
.PHONY: help setup sim pnr pnr-standalone pnr-openframe artifacts doctor check
help:
	@echo 'V0: make setup, make sim, make pnr, make artifacts, make doctor'
setup:
	$(PYTHON) scripts/v0.py setup
sim:
	$(PYTHON) scripts/v0.py sim
pnr:
	$(PYTHON) scripts/v0.py pnr
pnr-standalone:
	$(PYTHON) scripts/v0.py pnr-standalone
pnr-openframe:
	$(PYTHON) scripts/v0.py pnr-openframe
artifacts:
	$(PYTHON) scripts/v0.py artifacts
doctor:
	$(PYTHON) scripts/v0.py doctor
check:
	$(PYTHON) -m unittest discover -s scripts -p 'test_*.py'
