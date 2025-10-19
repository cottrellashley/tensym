# Makefile to run inside the DevContainer for python interpreter and dependencies setup
# Usage: make <target>
# Example: make install


# Variables
PIP=pip
VENV=.venv
REQUIREMENTS=requirements.txt


# Targets
.PHONY: all install test clean

all: install
	@echo "Setup complete. You can now activate the virtual environment with 'source $(VENV)/bin/activate'."
install: $(VENV)/bin/activate
	@echo "Installing dependencies..."
	$(PIP) install -r $(REQUIREMENTS)

$(VENV)/bin/activate: $(PYTHON)
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	touch $(VENV)/bin/activate
	@echo "Virtual environment created at $(VENV)."

