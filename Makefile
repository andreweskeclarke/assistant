.DEFAULT_GOAL = all

CONDA_ENV = ./env
CONDA_BIN = $(CONDA_ENV)/bin
PYTHON = PYTHONPATH=. $(CONDA_BIN)/python
CODE = ./assistant/ ./tests/
ACTIVATE = conda init bash && conda activate $(CONDA_ENV)

.PHONY: black
black:
	$(CONDA_BIN)/isort $(CODE)
	$(CONDA_BIN)/black $(CODE)

.PHONY: lint
lint: black
	$(CONDA_BIN)/pylint -j 0 $(CODE)
	$(CONDA_BIN)/flake8 $(CODE)

.PHONY: freeze
freeze:
	$(CONDA_BIN)/pip freeze > requirements.txt

.PHONY: test
test: lint
	$(PYTHON) -m unittest discover -s ./tests/

.PHONY: all
all: test freeze
	@echo "\n\033[1;32m--- SUCCESS ---\033[0m"

.PHONY: clean
clean:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

.PHONY: run
run:
	$(PYTHON) assistant/scripts/$(script).py