import asyncio
from io import BytesIO

import pytest
from fastapi import UploadFile, status
from PIL import Image
from starlette.datastructures import Headers

from app.utils.image_validation import (
    ImageValidationError,
    ImageValidationLimits,
    validate_uploaded_image,
)


def test_valid_image_is_accepted() -> None:
    image = _run_validation(_upload_file(_png_bytes(32, 24)))

    assert image.width == 32
    assert image.height == 24
    assert image.content_type == "image/png"


def test_image_width_above_limit_is_rejected() -> None:
    with pytest.raises(ImageValidationError) as exc_info:
        _run_validation(
            _upload_file(_png_bytes(11, 10)),
            ImageValidationLimits(
                max_upload_size_bytes=1024 * 1024,
                max_image_width=10,
                max_image_height=20,
                max_image_pixels=200,
            ),
        )

    assert exc_info.value.status_code == 413


def test_image_total_pixels_above_limit_is_rejected() -> None:
    with pytest.raises(ImageValidationError) as exc_info:
        _run_validation(
            _upload_file(_png_bytes(11, 10)),
            ImageValidationLimits(
                max_upload_size_bytes=1024 * 1024,
                max_image_width=20,
                max_image_height=20,
                max_image_pixels=100,
            ),
        )

    assert exc_info.value.status_code == 413


def test_non_image_file_is_rejected() -> None:
    with pytest.raises(ImageValidationError) as exc_info:
        _run_validation(_upload_file(b"not an image"))

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_empty_file_is_rejected() -> None:
    with pytest.raises(ImageValidationError) as exc_info:
        _run_validation(_upload_file(b""))

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def _run_validation(
    file: UploadFile,
    limits: ImageValidationLimits | None = None,
):
    return asyncio.run(
        validate_uploaded_image(file, limits or ImageValidationLimits())
    )


def _upload_file(
    data: bytes,
    filename: str = "board.png",
    content_type: str = "image/png",
) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=BytesIO(data),
        headers=Headers({"content-type": content_type}),
    )


def _png_bytes(width: int, height: int) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (width, height), color=(20, 80, 60)).save(
        buffer,
        format="PNG",
    )
    return buffer.getvalue()
