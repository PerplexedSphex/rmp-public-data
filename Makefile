.PHONY: help install test lint clean dev validate list-agents

help:
	@echo "Opsiary Makefile commands:"
	@echo "  install     Install dependencies"
	@echo "  test        Run tests"
	@echo "  lint        Run linting (flake8)"
	@echo "  clean       Clean up temporary files"
	@echo "  dev         Set up development environment"
	@echo "  validate    Validate all agents"
	@echo "  list-agents List all available agents"

install:
	pip install -r requirements.txt

test:
	pytest

lint:
	python -m flake8 .

clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf */*/*/__pycache__
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

dev: install
	cp -n config/.env.example config/.env || true
	@echo "Development environment set up. Edit config/.env with your API keys."

validate:
	@echo "Validating all agents..."
	@python -m cli.cli validate-agent email_summary_agent || exit 1
	@echo "All agents validated successfully!"

list-agents:
	python -m cli.cli list agents