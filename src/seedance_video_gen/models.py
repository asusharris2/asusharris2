from typing import Any

from pydantic import BaseModel, Field


class VideoGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: str | None = None
    duration_seconds: int = Field(default=5, ge=1, le=30)
    fps: int = Field(default=24, ge=1, le=60)
    width: int = Field(default=1280, ge=256)
    height: int = Field(default=720, ge=256)
    seed: int | None = None

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "prompt": self.prompt,
            "duration": self.duration_seconds,
            "fps": self.fps,
            "width": self.width,
            "height": self.height,
        }
        if self.negative_prompt:
            payload["negative_prompt"] = self.negative_prompt
        if self.seed is not None:
            payload["seed"] = self.seed
        return payload


class JobSubmissionResponse(BaseModel):
    request_id: str
    status_url: str


class JobStatusResponse(BaseModel):
    status: str
    response: dict[str, Any] | None = None
    error: dict[str, Any] | None = None


class VideoGenerationResult(BaseModel):
    request_id: str
    video_url: str
    raw_response: dict[str, Any]
