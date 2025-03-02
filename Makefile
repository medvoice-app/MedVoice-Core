SHELL := /bin/bash
DOCKER_FLAGS := up --build --scale worker=1
GPU ?= false

# Variables
NGROK_CONFIG_PATH := /home/laansdole/.config/ngrok/ngrok.yml
NGROK_EXAMPLE_FILE := $(NGROK_CONFIG_PATH).example

# Load environment variables from .env
ifneq (,$(wildcard .env))
    include .env
    export
endif

###############################################################################
# INSTALLATION COMMANDS
###############################################################################

# Run the main installation script to set up project dependencies
.PHONY: install
install: 
	@echo "Running installation script..."
	@chmod +x scripts/install.sh
	@./scripts/install.sh

# Create a Python virtual environment and install project dependencies 
.PHONY: venv-install
venv-install: install
	# Ensure Python3 and virtual environment
	@which python3 > /dev/null && python3 -m venv venv || python -m venv venv
	@echo "Setting up virtual environment and installing dependencies..."
	@bash -c "source venv/bin/activate && pip install -r requirements.txt && poetry install"
	@echo "Dependencies installed successfully."

# Complete setup: install dependencies and create environment file
.PHONY: venv-all
venv-all: venv-install env-secrets

# Install NVIDIA toolkit for GPU support
.PHONY: nvidia
nvidia: 
	@echo "Running installation script..."
	@chmod +x scripts/install_nvidia_toolkit.sh
	@./scripts/install_nvidia_toolkit.sh

###############################################################################
# ENVIRONMENT SETUP
###############################################################################

# Create environment file from template and open it for editing
.PHONY: env-secrets
env-secrets:
	@echo "Creating .env file..."
	@envsubst < .env.example > .env
	@echo ".env file has been created!"
	@vi .env

# Create ngrok configuration file from template
.PHONY: ngrok
ngrok:
	@echo "Creating ngrok.yml configuration file..."
	@envsubst < ngrok.example.yml > ngrok.yml
	@echo "ngrok.yml file has been created!"

###############################################################################
# DOCKER COMMANDS
###############################################################################

# Start the project using Docker Compose with optional GPU support
.PHONY: up
up:
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
# UTILITY COMMANDS
###############################################################################

# Verify system dependencies and required configuration files
.PHONY: check
check:
	@echo "Checking system dependencies and required files..."
	@echo ""
	@which docker-compose > /dev/null && echo "✔ docker-compose is installed." || echo "✘ docker-compose is not installed. Please install it."
	@echo ""
	@which docker > /dev/null && echo "✔ Docker is installed." || echo "✘ Docker is not installed. Please install it."
	@echo ""
	@which python > /dev/null && echo "✔ Python is installed." || echo "✘ Python is not installed. Please install it. Ignore this if you have python3 installed."
	@echo ""
	@which ngrok > /dev/null && echo "✔ ngrok is installed." || echo "✘ ngrok is not installed. Please install it."
	@echo ""
	@test -f .env && echo "✔ .env file exists." || echo "✘ .env file is missing. Please see .env.example for reference and add it."
	@echo ""
	@test -f google-credentials.json && echo "✔ google-credentials.json file exists." || echo "✘ google-credentials.json file is missing. Please see google-credentials.example.json for reference and add it."
	@echo ""
	@test -f ngrok.yml && echo "✔ ngrok.yml file exists." || echo "✘ ngrok.yml file is missing. Please see ngrok.example.yml for reference and add it."
	@echo ""
	@echo "System check complete. If you are running the project in Ubuntu, run make install to setup the project."
