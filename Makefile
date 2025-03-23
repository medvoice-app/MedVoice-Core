SHELL := /bin/bash
DOCKER_FLAGS := up --build --scale worker=1
GPU ?= false

# Load environment variables from .env
ifneq (,$(wildcard .env))
    include .env
    export
endif

###############################################################################
# INSTALLATION COMMANDS
###############################################################################

# Install basic system dependencies (Docker, Python, etc.)
.PHONY: install
install: 
	@echo "Running installation script..."
	@chmod +x scripts/install.sh
	@./scripts/install.sh

# Create a Python virtual environment and install project dependencies 
.PHONY: setup
setup:
	# Ensure Python3 and virtual environment
	@which python3 > /dev/null && python3 -m venv venv || python -m venv venv
	@echo "Setting up virtual environment and installing dependencies..."
	@bash -c "source venv/bin/activate && pip install -r requirements.txt && poetry install"
	@echo "Creating default .env file..."
	@cp -n .env.example .env || true
	@echo "Installing test dependencies..."
	@$(MAKE) setup-tests
	@echo "Setup completed successfully."

# Install test dependencies
.PHONY: setup-tests
setup-tests:
	@echo "Installing test dependencies..."
	@bash -c "pip install pytest pytest-asyncio pytest-cov aiosqlite"

# Install NVIDIA toolkit for GPU support (optional)
.PHONY: nvidia
nvidia: 
	@echo "Installing NVIDIA toolkit for GPU support..."
	@chmod +x scripts/install_nvidia_toolkit.sh
	@./scripts/install_nvidia_toolkit.sh

###############################################################################
# DOCKER COMMANDS
###############################################################################

# Generate Docker environment files from configuration
.PHONY: generate-env
generate-env:
	@echo "Generating Docker environment files from configuration..."
	@python scripts/generate_env_files.py

# Start the project using Docker Compose with optional GPU support
.PHONY: up
up: generate-env
	@if [ "$(GPU)" = "true" ]; then \
		echo "Starting with GPU support..."; \
		sudo lsof -i :11434; \
		if command -v docker-compose >/dev/null 2>&1; then \
			docker-compose -f docker-compose.yml -f ./docker/docker-compose.gpu.yml $(DOCKER_FLAGS); \
		else \
			docker compose -f docker-compose.yml -f ./docker/docker-compose.gpu.yml $(DOCKER_FLAGS); \
		fi; \
	else \
		echo "Starting without GPU support..."; \
		if command -v docker-compose >/dev/null 2>&1; then \
			docker-compose $(DOCKER_FLAGS); \
		else \
			docker compose $(DOCKER_FLAGS); \
		fi; \
	fi
	@echo "Project started."

# Stop all Docker Compose services
.PHONY: down
down:
	@if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose down; \
	else \
		docker compose down; \
	fi
	@echo "Project stopped."

###############################################################################
# TESTS COMMANDS
###############################################################################

# Run only nurse API tests (excluding LLM tests)
.PHONY: test-api
test-api:
	@echo "Running API tests only (excluding LLM tests)..."
	@bash -c "python -m pytest tests/integration/test_nurse_api.py tests/integration/test_db.py -v"

# Run tests with coverage report excluding LLM tests
.PHONY: test-coverage-api
test-coverage-api:
	@echo "Running API tests with coverage report (excluding LLM tests)..."
	@bash -c "python -m pytest tests/integration/test_nurse_api.py tests/integration/test_db.py --cov=app --cov-report=term-missing -v"

# Run tests with debug info
.PHONY: test-debug
test-debug:
	@echo "Running tests with debug information..."
	@bash -c "python -m pytest tests/integration/test_nurse_api.py -v --no-header --showlocals"

###############################################################################
# UTILITY COMMANDS
###############################################################################

# Verify system dependencies
.PHONY: check
check:
	@echo "Checking system dependencies and required files..."
	@echo ""
	@which docker-compose > /dev/null && echo "✔ docker-compose is installed." || echo "✘ docker-compose is not installed. Please install it."
	@echo ""
	@which docker > /dev/null && echo "✔ Docker is installed." || echo "✘ Docker is not installed. Please install it."
	@echo ""
	@which python3 > /dev/null && echo "✔ Python3 is installed." || echo "✘ Python3 is not installed. Please install it."
	@echo ""
	@echo "System check complete. If you are missing dependencies, run 'make install' to install them."

# Configure ngrok for remote access (optional)
.PHONY: ngrok
ngrok:
	@echo "Creating ngrok configuration..."
	@cp -n ngrok.example.yml ngrok.yml || true
	@echo "Edit ngrok.yml with your configuration details."

# Export dependencies to requirements.txt
.PHONY: export
export:
	@echo "Exporting dependencies to requirements.txt..."
	@poetry export -f requirements.txt --output requirements.txt --without-hashes

# Import dependencies from requirements.txt to poetry
.PHONY: import
import:
	@echo "Importing dependencies from requirements.txt..."
	@python3 scripts/pip_to_poetry_pkg.py

# Clean temporary files and directories
.PHONY: clean
clean:
	@echo "Cleaning temporary files and directories..."
	@python3 scripts/empty_dir.py
