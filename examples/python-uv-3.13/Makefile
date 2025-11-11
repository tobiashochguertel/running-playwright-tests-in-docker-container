.PHONY: help build test test-verbose test-single report shell clean

help:
	@echo "Available commands:"
	@echo "  make build           - Build Docker image"
	@echo "  make test            - Run all tests"
	@echo "  make test-verbose    - Run tests with verbose output"
	@echo "  make test-single     - Run a specific test file (use FILE=tests/test_google.py)"
	@echo "  make report          - Generate and open HTML report"
	@echo "  make shell           - Open interactive shell in container"
	@echo "  make clean           - Remove containers and artifacts"

build:
	docker-compose build

test:
	docker-compose run --rm playwright pytest -v tests/

test-verbose:
	docker-compose run --rm playwright pytest -vv --tb=long tests/

test-single:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make test-single FILE=tests/test_google.py"; \
		exit 1; \
	fi
	docker-compose run --rm playwright pytest -vv $(FILE)

report: test
	@if command -v open &> /dev/null; then \
		open htmlreport/report.html; \
	elif command -v xdg-open &> /dev/null; then \
		xdg-open htmlreport/report.html; \
	else \
		echo "HTML report generated at: htmlreport/report.html"; \
	fi

shell:
	docker-compose run --rm playwright /bin/bash

clean:
	docker-compose down
	rm -rf htmlreport test-results __pycache__ .pytest_cache
	@echo "✅ Cleaned up Docker containers and artifacts"
