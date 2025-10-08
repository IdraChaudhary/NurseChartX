# Contributing to NurseChartX

We welcome contributions from the community! This document outlines the process for contributing to the NurseChartX project.

## Development Environment Setup

1. Fork the repository
2. Clone your fork locally
3. Set up Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

nstall pre-commit hooks:

bash
pre-commit install

Code Style
Follow PEP 8 guidelines

Use type hints for all function signatures

Write docstrings for all public functions and classes

Maximum line length: 88 characters (Black formatter)

Testing
Write tests for new functionality

Ensure all tests pass before submitting PR

Run tests: pytest tests/

Test coverage: pytest --cov=src tests/

Pull Request Process
Create a feature branch from main

Make your changes with clear commit messages

Add or update tests as needed

Update documentation if required

Ensure CI checks pass

Submit PR with clear description of changes

Issue Reporting
Use the issue templates

Provide reproduction steps for bugs

For feature requests, explain the use case and benefits

License
By contributing, you agree that your contributions will be licensed under the MIT License.
