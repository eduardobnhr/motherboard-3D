"""Application configuration for the motherboard analysis backend."""

from functools import lru_cache
from os import environ, getenv
from pathlib import Path

from app.utils.image_validation import (
    DEFAULT_MAX_IMAGE_HEIGHT,
    DEFAULT_MAX_IMAGE_PIXELS,
    DEFAULT_MAX_IMAGE_WIDTH,
    DEFAULT_MAX_UPLOAD_SIZE_BYTES,
    ImageValidationLimits,
)

DEFAULT_OPENAI_MODEL = "gpt-4o"
DEFAULT_OPENAI_TIMEOUT_SECONDS = 60.0
DEFAULT_CORS_ALLOWED_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)
BACKEND_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


class Settings:
    """Runtime settings read from environment variables."""

    app_name: str = "Motherboard 3D API"
    api_prefix: str = "/api"
    max_image_upload_bytes: int
    max_image_width: int
    max_image_height: int
    max_image_pixels: int
    openai_api_key: str | None
    openai_model: str
    openai_timeout_seconds: float
    use_mock_analyzer: bool
    cors_allowed_origins: list[str]

    def __init__(self) -> None:
        self.max_image_upload_bytes = int(
            getenv(
                "MAX_UPLOAD_SIZE_BYTES",
                getenv("MAX_IMAGE_UPLOAD_BYTES", DEFAULT_MAX_UPLOAD_SIZE_BYTES),
            )
        )
        self.max_image_width = int(
            getenv("MAX_IMAGE_WIDTH", DEFAULT_MAX_IMAGE_WIDTH)
        )
        self.max_image_height = int(
            getenv("MAX_IMAGE_HEIGHT", DEFAULT_MAX_IMAGE_HEIGHT)
        )
        self.max_image_pixels = int(
            getenv("MAX_IMAGE_PIXELS", DEFAULT_MAX_IMAGE_PIXELS)
        )
        self.openai_api_key = getenv("OPENAI_API_KEY")
        self.openai_model = getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        self.openai_timeout_seconds = float(
            getenv("OPENAI_TIMEOUT_SECONDS", DEFAULT_OPENAI_TIMEOUT_SECONDS)
        )
        self.use_mock_analyzer = _read_bool("USE_MOCK_ANALYZER", default=False)
        self.cors_allowed_origins = _read_csv_list(
            "CORS_ALLOWED_ORIGINS",
            DEFAULT_CORS_ALLOWED_ORIGINS,
        )

    @property
    def image_validation_limits(self) -> ImageValidationLimits:
        """Return upload safety limits for image validation."""

        return ImageValidationLimits(
            max_upload_size_bytes=self.max_image_upload_bytes,
            max_image_width=self.max_image_width,
            max_image_height=self.max_image_height,
            max_image_pixels=self.max_image_pixels,
        )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    _load_env_file(BACKEND_ENV_PATH)
    return Settings()


def _read_bool(name: str, default: bool) -> bool:
    value = getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _read_csv_list(name: str, default: tuple[str, ...]) -> list[str]:
    value = getenv(name)
    if value is None:
        return list(default)

    items = [
        item.strip()
        for item in value.split(",")
        if item.strip() and item.strip() != "*"
    ]

    return items or list(default)


def _load_env_file(path: Path) -> None:
    """Load backend/.env values without overriding existing environment vars."""

    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in environ:
            environ[key] = value
