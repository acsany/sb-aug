# secondbrain

## Installation

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd secondbrain
uv sync
```

## Usage

Via the CLI entrypoint:

```bash
uv run secondbrain
```

With the dev environment loaded:

```bash
uv run --env-file .env secondbrain
```

Via the Python module:

```bash
uv run python -m secondbrain
```

## Environment Variables

`.env.example` is the template for local configuration — copy it to `.env` for development:

```bash
cp .env.example .env
```

- `LOG_LEVEL` (default: `INFO`) — set to `DEBUG` in `.env` for verbose console output.
- `LOG_FILE` (default: `app.log`) — path to the log file.

`.env` is not auto-loaded; use `uv run --env-file .env` to load the dev environment explicitly.

## Testing

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov
```

## Documentation

Preview docs locally:

```bash
uv run python scripts/serve_docs.py
```

Build static docs:

```bash
uv run mkdocs build
```
