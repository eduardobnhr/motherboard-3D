"""Validation and parsing helpers for uploaded motherboard images."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile, status
from PIL import Image, UnidentifiedImageError


ALLOWED_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg"})
ALLOWED_IMAGE_MIME_TYPES = frozenset({"image/png", "image/jpeg", "image/jpg"})


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


async def validate_uploaded_image(
    file: UploadFile,
    max_size_bytes: int,
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

    data = await _read_limited_upload(file, max_size_bytes)
    if not data:
        raise ImageValidationError("Uploaded image file is empty.")

    width, height = _read_image_dimensions(data)

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
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        chunks.append(chunk)

    return b"".join(chunks)


def _read_image_dimensions(data: bytes) -> tuple[int, int]:
    """Parse image bytes and return trusted pixel dimensions."""

    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()

        with Image.open(BytesIO(data)) as image:
            return image.size
    except UnidentifiedImageError as exc:
        raise ImageValidationError("Uploaded file is not a valid image.") from exc
    except OSError as exc:
        raise ImageValidationError("Uploaded image could not be read.") from exc

