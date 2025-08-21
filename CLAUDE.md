# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project called "hydra" that uses Poetry for dependency management and packaging. The project appears to be in early development stages with mostly empty source files.

## Development Commands

This project uses Poetry as the build system. Common commands:

- `poetry install` - Install dependencies
- `poetry build` - Build the package
- `poetry run python -m pytest` - Run tests
- `poetry shell` - Activate virtual environment

## Architecture

The codebase follows a modular structure:

- `src/hydra/` - Main package directory
- `src/hydra/core/` - Core functionality modules
  - `agent/` - Agent-related functionality
  - `managed/` - Managed services (node.py, service.py)
  - `webserver/` - Web server components
- `src/hydra/config/` - Configuration files (configuration.yaml)
- `tests/` - Test directory

## Project Configuration

- Python 3.12+ required
- Uses Poetry for dependency management (`pyproject.toml`)
- Package structure defined with `src/` layout
- Empty README.md file exists but contains no content

## Development Notes

- Most source files are currently empty placeholders
- The project structure suggests this will be a distributed system with agents, managed services, and a web interface
- Configuration is handled via YAML files in the config directory