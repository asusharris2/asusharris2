import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure application logging with a production-friendly format."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )
