# Mealie Toolkit

A Python project for managing and categorizing Mealie recipes using AI.

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

- `fetch-recipes` - Fetch and list all recipes from your Mealie instance
- `fetch-categories` - Fetch and list all categories from your Mealie instance
- `auto-categorize-recipes` - Auto-categorize recipes using AI (with optional `--limit` for debugging)
- `populate-categories` - Add categories from a file (one per line)

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
├── mealie_toolkit/        # Main package
│   ├── __init__.py
│   ├── main.py
│   ├── mealie_client.py
│   └── categorizer_client.py
├── tests/                 # Test directory
│   ├── conftest.py
│   └── test_example.py
├── .env.example           # Environment variables template
├── pyproject.toml         # Project configuration
├── Makefile               # Build targets
└── README.md              # This file
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
