# Usage

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Running

Via the CLI entrypoint:

```bash
uv run secondbrain                          # production defaults
uv run --env-file .env secondbrain          # dev settings
```

Or as a Python module:

```bash
uv run python -m secondbrain
```

## Environment Variables

| Variable    | Default    | Description                          |
|-------------|------------|---------------------------------------|
| `LOG_LEVEL` | `INFO`     | Console log level (DEBUG, INFO, …)   |
| `LOG_FILE`  | `app.log`  | Path to the log file                 |

Copy `.env.example` to `.env` for development defaults, then run with `uv run --env-file .env`.

## Logging

Console and file handlers share one compact, pipe-delimited format:

```
2026-08-01 20:56:47 | I | secondbrain.app:main:29 | Hello from secondbrain!
```

Timestamps carry no milliseconds and the level is a single-letter code, so lines stay
column-aligned:

```text
"<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
"<level>{level.icon}</level> | "
"<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
"<level>{message}</level>"
```

The colour markup is stripped for non-colorized sinks, so `app.log` lines are byte-identical
to the console lines.

| Level      | Icon |
|------------|------|
| `TRACE`    | `T`  |
| `DEBUG`    | `D`  |
| `INFO`     | `I`  |
| `SUCCESS`  | `S`  |
| `WARNING`  | `W`  |
| `ERROR`    | `E`  |
| `CRITICAL` | `C`  |
