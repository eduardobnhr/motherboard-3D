"""Validation and parsing helpers for uploaded motherboard images."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import warnings

from fastapi import UploadFile, status
from PIL import Image, UnidentifiedImageError


ALLOWED_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg"})
ALLOWED_IMAGE_MIME_TYPES = frozenset({"image/png", "image/jpeg", "image/jpg"})
DEFAULT_MAX_UPLOAD_SIZE_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_IMAGE_WIDTH = 8192
DEFAULT_MAX_IMAGE_HEIGHT = 8192
DEFAULT_MAX_IMAGE_PIXELS = 24_000_000
HTTP_413_CONTENT_TOO_LARGE = getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413)


class ImageValidationError(ValueError):
    """Validation error that can be translated to an HTTP response."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class ValidatedImage:
    """Uploaded image bytes plus metadata needed by the analysis service."""

    filename: str
    content_type: str
    data: bytes
    width: int
    height: int


@dataclass(frozen=True)
class ImageValidationLimits:
    """Configurable safety limits for uploaded image validation."""

    max_upload_size_bytes: int = DEFAULT_MAX_UPLOAD_SIZE_BYTES
    max_image_width: int = DEFAULT_MAX_IMAGE_WIDTH
    max_image_height: int = DEFAULT_MAX_IMAGE_HEIGHT
    max_image_pixels: int = DEFAULT_MAX_IMAGE_PIXELS


async def validate_uploaded_image(
    file: UploadFile,
    limits: ImageValidationLimits,
) -> ValidatedImage:
    """Validate an uploaded image and return its bytes and dimensions."""

    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ImageValidationError(
            "Unsupported file extension. Use PNG, JPG, or JPEG."
        )

    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ImageValidationError(
            "Unsupported image MIME type. Use image/png or image/jpeg."
        )

    data = await _read_limited_upload(file, limits.max_upload_size_bytes)
    if not data:
        raise ImageValidationError("Uploaded image file is empty.")

    width, height = _read_image_dimensions(data)
    _validate_image_dimensions(width, height, limits)

    return ValidatedImage(
        filename=filename,
        content_type=content_type,
        data=data,
        width=width,
        height=height,
    )


async def _read_limited_upload(file: UploadFile, max_size_bytes: int) -> bytes:
    """Read an UploadFile while enforcing a maximum byte size."""

    chunks: list[bytes] = []
    total_size = 0
    chunk_size = 1024 * 1024

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break

        total_size += len(chunk)
        if total_size > max_size_bytes:
            raise ImageValidationError(
                f"Uploaded image exceeds the {max_size_bytes} byte limit.",
                HTTP_413_CONTENT_TOO_LARGE,
            )

        chunks.append(chunk)

    return b"".join(chunks)


def _read_image_dimensions(data: bytes) -> tuple[int, int]:
    """Parse image bytes and return trusted pixel dimensions."""

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)

            with Image.open(BytesIO(data)) as image:
                image.verify()

            with Image.open(BytesIO(data)) as image:
                return image.size
    except Image.DecompressionBombError as exc:
        raise ImageValidationError(
            "Uploaded image is too large to process safely.",
            HTTP_413_CONTENT_TOO_LARGE,
        ) from exc
    except Image.DecompressionBombWarning as exc:
        raise ImageValidationError(
            "Uploaded image is too large to process safely.",
            HTTP_413_CONTENT_TOO_LARGE,
        ) from exc
    except UnidentifiedImageError as exc:
        raise ImageValidationError("Uploaded file is not a valid image.") from exc
    except OSError as exc:
        raise ImageValidationError("Uploaded image could not be read.") from exc


def _validate_image_dimensions(
    width: int,
    height: int,
    limits: ImageValidationLimits,
) -> None:
    """Validate dimensions and total pixels against configured safety limits."""

    if width <= 0 or height <= 0:
        raise ImageValidationError("Uploaded image has invalid dimensions.")

    if width > limits.max_image_width:
        raise ImageValidationError(
            f"Uploaded image width exceeds the {limits.max_image_width}px limit.",
            HTTP_413_CONTENT_TOO_LARGE,
        )

    if height > limits.max_image_height:
        raise ImageValidationError(
            f"Uploaded image height exceeds the {limits.max_image_height}px limit.",
            HTTP_413_CONTENT_TOO_LARGE,
        )

    total_pixels = width * height
    if total_pixels > limits.max_image_pixels:
        raise ImageValidationError(
            (
                "Uploaded image total pixels exceed the "
                f"{limits.max_image_pixels}px limit."
            ),
            HTTP_413_CONTENT_TOO_LARGE,
        )
