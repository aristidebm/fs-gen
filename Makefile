.DEFAULT_GOAL := help
.PHONY := help install install-dev

install: ## Install project dependencies.
	@echo "Installing project dependencies."
	pip install -r requirements.txt

install-dev: ## Install dev dependencies.
	@echo "Installing dev dependencies."
	pip install -r requirements-dev.txt

codestyle: ## Execute python styling check on project.
	flake8 main.py utils.py
	black main.py utils.py

help: ## Show this help page.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
