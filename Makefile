PYTHON ?= python3
.PHONY: setup unit isolation test baseline up down contract
setup:
	$(PYTHON) -m pip install -r requirements.txt
unit:
	$(PYTHON) -m pytest -q tests/baseline
isolation:
	$(PYTHON) -m pytest -q tests/isolation
test:
	$(PYTHON) -m pytest -q tests
contract:
	$(PYTHON) scripts/check_contract.py
baseline:
	$(PYTHON) scripts/replay_m01.py
up:
	docker compose up -d --build
down:
	docker compose down --volumes
