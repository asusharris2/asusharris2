import logging
from typing import Any

import httpx

from .config import Settings
from .errors import APIRequestError
from .models import JobStatusResponse, JobSubmissionResponse, VideoGenerationRequest

logger = logging.getLogger(__name__)


class FalSeedanceClient:
    """Async client for the fal.ai queue API."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.fal_base_url,
            timeout=settings.request_timeout_seconds,
            headers={
                "Authorization": f"Key {settings.fal_api_key}",
                "Content-Type": "application/json",
            },
        )

    async def __aenter__(self) -> "FalSeedanceClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def submit_generation(self, request: VideoGenerationRequest) -> JobSubmissionResponse:
        endpoint = f"/{self.settings.fal_model}"
        payload = request.to_payload()
        logger.info("Submitting generation request to %s", endpoint)
        response = await self._client.post(endpoint, json=payload)
        if response.status_code >= 400:
            raise APIRequestError(f"Failed to submit job: {response.status_code} {response.text}")

        data: dict[str, Any] = response.json()
        request_id = data.get("request_id")
        if not request_id:
            raise APIRequestError(f"Submission response missing request_id: {data}")

        status_url = f"/{self.settings.fal_model}/requests/{request_id}/status"
        return JobSubmissionResponse(request_id=request_id, status_url=status_url)

    async def get_job_status(self, status_url: str) -> JobStatusResponse:
        response = await self._client.get(status_url)
        if response.status_code >= 400:
            raise APIRequestError(f"Failed to poll job: {response.status_code} {response.text}")
        data: dict[str, Any] = response.json()
        return JobStatusResponse.model_validate(data)

    async def get_result(self, request_id: str) -> dict[str, Any]:
        result_url = f"/{self.settings.fal_model}/requests/{request_id}"
        response = await self._client.get(result_url)
        if response.status_code >= 400:
            raise APIRequestError(f"Failed to fetch result: {response.status_code} {response.text}")
        return response.json()
