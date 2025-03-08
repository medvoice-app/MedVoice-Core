# Contributing to MedVoice-FastAPI

Thank you for your interest in contributing to MedVoice-FastAPI! This document outlines the process for contributing to the project.

## Development Setup

### Prerequisites
- Python 3.10+
- Poetry (dependency management)
- Git
- Docker and Docker Compose (for local development)
- Make

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/MedVoice-RMIT-CapStone-2024/MedVoice-FastAPI.git
   cd MedVoice-FastAPI
   ```

2. Install dependencies using Make:
   ```bash
   make venv-all
   ```

3. Set up Google Cloud credentials:
   - Follow instructions in `/docs/how-to-setup-gcp-service-account.md`
   - Rename `google-credentials.example.json` to `google-credentials.json` and add your credentials

4. Configure environment variables:
   - Copy `.env.example` to `.env` and update with your values

5. Start the development server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

   Or using Docker:
   ```bash
   make GPU=false up
   ```

## Contribution Workflow

1. Create a new branch from `dev`:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following the coding standards below

3. Write tests for your changes

4. Commit your changes using conventional commit messages:
   ```bash
   git commit -m "feat: add new feature"
   ```

5. Push your branch and create a pull request to the `dev` branch:
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Process

1. Ensure your PR includes a description of the changes and the purpose
2. Update documentation if necessary
3. Make sure all linting passes
4. Request a review from a project maintainer
5. Address any requested changes
6. Once approved, your PR will be merged

## Coding Standards

### Python Style Guide
- Follow PEP 8 conventions
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep line length to a maximum of 100 characters

### Project Structure
- API endpoints in `/app/api/v1/endpoints`
- Database models in `/app/models`
- Schemas in `/app/schemas`
- Utility functions in `/app/utils`

### Commit Messages
Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `feat:` for new features
- `fix:` for bug fixes
- `chore:` for maintenance tasks
- `docs:` for documentation changes
- `refactor:` for code refactoring
- `test:` for adding or modifying tests

## License
By contributing to this project, you agree that your contributions will be licensed under the project's GNU GENERAL PL License (see LICENSE file).