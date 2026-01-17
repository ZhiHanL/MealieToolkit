# Mealie Toolkit

A Python toolkit for managing and categorizing Mealie recipes using AI. This project leverages Ollama to automatically categorize recipes and apply tags based on recipe content.

## Features

- **AI-Powered Categorization** - Automatically categorize recipes using local Ollama AI
- **Smart Tagging** - Auto-tag recipes using local Ollama AI
- **Recipe Management** - Fetch and display all recipes from your Mealie instance
- **Category Management** - View and populate categories

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

### Installation

```bash
make install
```

### Development

Install development dependencies:

```bash
make dev
```

## Usage

```bash
uv run python mealie_toolkit/main.py --help
```

## Available Commands

### Recipe Operations
- `fetch-recipes` - Fetch and list all recipes from your Mealie instance
- `auto-tag --tag <TAG> [--limit N]` - Auto-tag recipes based on a given tag (e.g., vegetarian, quick, spicy) using Ollama AI suggestions
  - Requires the tag to be created in Mealie beforehand

### Category Operations
- `fetch-categories` - Fetch and list all categories from your Mealie instance
- `auto-categorize-recipes [--limit N]` - Auto-categorize recipes using Ollama AI suggestions
- `populate-categories --file <PATH>` - Add categories from a file (one per line)

### Examples

Auto-categorize all recipes:
```bash
uv run python mealie_toolkit/main.py auto-categorize-recipes
```

Auto-categorize with a limit (useful for testing):
```bash
uv run python mealie_toolkit/main.py auto-categorize-recipes --limit 10
```

Auto-tag vegetarian recipes:
```bash
uv run python mealie_toolkit/main.py auto-tag --tag vegetarian
```

Populate categories from a file:
```bash
uv run python mealie_toolkit/main.py populate-categories --file categories.txt
```

## Development Commands

- `make lint` - Run linting checks with ruff
- `make format` - Format code with black
- `make type-check` - Run type checking with mypy
- `make test` - Run tests with pytest
- `make clean` - Remove build artifacts and cache
- `make all` - Run install, lint, format, and test

## Project Structure

```
.
├── mealie_toolkit/          # Main package
│   ├── __init__.py
│   ├── main.py             # CLI entry point
│   ├── mealie_client.py    # Mealie API client
│   ├── ollama_client.py    # Ollama AI client
│   ├── categorize.py       # Auto-categorization logic
│   ├── tagging.py          # Auto-tagging logic
│   └── utils.py            # Utility functions
├── tests/                   # Test directory
│   ├── conftest.py
│   └── test_example.py
├── .env.example            # Environment variables template
├── pyproject.toml          # Project configuration
├── Makefile                # Build targets
└── README.md               # This file
```

## Configuration

Create a `.env` file based on `.env.example`:

```bash
MEALIE_URL=https://your-mealie-instance.com
MEALIE_API_TOKEN=your-api-token
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:12b
```

## License
MIT
