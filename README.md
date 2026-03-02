# Seedance Video Generation System (fal.ai)

Production-ready Python system for AI video generation with **fal.ai Seedance 2.0** featuring:

- Modular architecture
- Async processing (submission + polling)
- Config management via environment variables
- Structured logging
- Robust error handling
- CLI interface

## Project structure

```text
src/seedance_video_gen/
  config.py          # Environment-based settings
  logging_config.py  # Logging setup
  errors.py          # Domain exceptions
  models.py          # Typed request/response models
  fal_client.py      # Async fal.ai API client
  service.py         # Business workflow orchestration
  cli.py             # Typer CLI
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

Set environment variables:

```bash
export FAL_API_KEY="your_fal_api_key"
export FAL_MODEL="fal-ai/seedance/v2"
# Optional overrides
export FAL_BASE_URL="https://fal.run"
export REQUEST_TIMEOUT_SECONDS=30
export POLL_INTERVAL_SECONDS=2
export MAX_POLL_SECONDS=600
export LOG_LEVEL="INFO"
```

## Usage

```bash
seedance generate \
  --prompt "cinematic drone shot of a futuristic city at sunrise" \
  --duration 6 \
  --fps 24 \
  --width 1280 \
  --height 720 \
  --output artifacts/result.json
```

The command prints the full response JSON and extracts `video_url` for downstream workflows.

## Notes for production hardening

- Add retries/backoff around transient HTTP status codes (429/5xx).
- Add centralized log aggregation.
- Add secret management (Vault/SM) instead of plain env vars.
- Add queueing and worker pools for high throughput.
