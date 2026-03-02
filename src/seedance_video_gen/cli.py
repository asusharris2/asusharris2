import asyncio
import json
import logging
from pathlib import Path

import typer

from .config import get_settings
from .errors import VideoGenerationError
from .logging_config import configure_logging
from .models import VideoGenerationRequest
from .service import VideoGenerationService

app = typer.Typer(help="Generate AI videos with fal.ai Seedance 2.0")
logger = logging.getLogger(__name__)


@app.command()
def generate(
    prompt: str = typer.Option(..., "--prompt", help="Primary generation prompt."),
    output: Path | None = typer.Option(None, "--output", help="Optional JSON output file path."),
    negative_prompt: str | None = typer.Option(None, "--negative-prompt"),
    duration_seconds: int = typer.Option(5, "--duration", min=1, max=30),
    fps: int = typer.Option(24, "--fps", min=1, max=60),
    width: int = typer.Option(1280, "--width", min=256),
    height: int = typer.Option(720, "--height", min=256),
    seed: int | None = typer.Option(None, "--seed"),
) -> None:
    """Submit a video generation request and wait for completion."""
    settings = get_settings()
    configure_logging(settings.log_level)

    request = VideoGenerationRequest(
        prompt=prompt,
        negative_prompt=negative_prompt,
        duration_seconds=duration_seconds,
        fps=fps,
        width=width,
        height=height,
        seed=seed,
    )

    service = VideoGenerationService(settings)

    try:
        result = asyncio.run(service.generate_video(request))
    except VideoGenerationError as exc:
        logger.error("Video generation failed: %s", exc)
        raise typer.Exit(code=1) from exc

    payload = result.model_dump()
    typer.echo(json.dumps(payload, indent=2))

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Saved result payload to %s", output)


if __name__ == "__main__":
    app()
