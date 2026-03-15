PYTHON ?= python
PIP := $(PYTHON) -m pip

.PHONY: clean install test run migrate migrate-create lint

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

install:
	$(PIP) install -r backend/requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests -v

run:
	$(PYTHON) -m uvicorn app:app --reload

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(msg)"

lint:
	ruff check .
