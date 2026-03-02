import asyncio
import logging
import time

from .config import Settings
from .errors import APIRequestError, JobTimeoutError, VideoGenerationError
from .fal_client import FalSeedanceClient
from .models import VideoGenerationRequest, VideoGenerationResult

logger = logging.getLogger(__name__)


class VideoGenerationService:
    """Orchestrates asynchronous generation and polling flow."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        started = time.monotonic()
        async with FalSeedanceClient(self.settings) as client:
            submission = await client.submit_generation(request)
            logger.info("Job accepted with request_id=%s", submission.request_id)

            while True:
                elapsed = time.monotonic() - started
                if elapsed > self.settings.max_poll_seconds:
                    raise JobTimeoutError(
                        f"Timed out waiting for request_id={submission.request_id} after {elapsed:.1f}s"
                    )

                status = await client.get_job_status(submission.status_url)
                state = status.status.lower()
                logger.info("request_id=%s current_status=%s", submission.request_id, state)

                if state == "completed":
                    raw = await client.get_result(submission.request_id)
                    video_url = self._extract_video_url(raw)
                    return VideoGenerationResult(
                        request_id=submission.request_id,
                        video_url=video_url,
                        raw_response=raw,
                    )

                if state in {"failed", "error", "cancelled"}:
                    raise VideoGenerationError(f"Job {submission.request_id} failed: {status.error}")

                await asyncio.sleep(self.settings.poll_interval_seconds)

    @staticmethod
    def _extract_video_url(result_payload: dict) -> str:
        """Attempt to extract a video URL from common fal.ai response schemas."""
        for key in ("video", "output", "result"):
            value = result_payload.get(key)
            if isinstance(value, dict):
                url = value.get("url")
                if isinstance(url, str) and url:
                    return url
            if isinstance(value, list) and value:
                first = value[0]
                if isinstance(first, dict):
                    url = first.get("url")
                    if isinstance(url, str) and url:
                        return url

        for key in ("video_url", "url"):
            val = result_payload.get(key)
            if isinstance(val, str) and val:
                return val

        raise APIRequestError(f"No video URL found in result payload: {result_payload}")
