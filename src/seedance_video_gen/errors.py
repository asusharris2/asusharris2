class VideoGenerationError(Exception):
    """Base exception for video generation failures."""


class APIRequestError(VideoGenerationError):
    """Raised when fal.ai returns a non-successful response."""


class JobTimeoutError(VideoGenerationError):
    """Raised when generation polling exceeds the configured timeout."""
