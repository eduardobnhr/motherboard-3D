"""Application configuration for the motherboard analysis backend."""

from functools import lru_cache
from os import getenv


DEFAULT_MAX_IMAGE_UPLOAD_BYTES = 8 * 1024 * 1024


class Settings:
    """Runtime settings read from environment variables."""

    app_name: str = "Motherboard 3D API"
    api_prefix: str = "/api"
    max_image_upload_bytes: int

    def __init__(self) -> None:
        self.max_image_upload_bytes = int(
            getenv("MAX_IMAGE_UPLOAD_BYTES", DEFAULT_MAX_IMAGE_UPLOAD_BYTES)
        )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()

