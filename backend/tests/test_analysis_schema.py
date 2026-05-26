import pytest
from pydantic import ValidationError

from app.schemas.analysis import MotherboardAnalysisResponse


def test_valid_bboxes_are_accepted() -> None:
    response = MotherboardAnalysisResponse.model_validate(_payload())

    assert response.board.bbox.width == 80
    assert response.components[0].bbox.x == 20


def test_board_bbox_with_negative_x_is_rejected() -> None:
    payload = _payload()
    payload["board"]["bbox"]["x"] = -1

    with pytest.raises(ValidationError):
        MotherboardAnalysisResponse.model_validate(payload)


def test_board_bbox_with_negative_y_is_rejected() -> None:
    payload = _payload()
    payload["board"]["bbox"]["y"] = -1

    with pytest.raises(ValidationError):
        MotherboardAnalysisResponse.model_validate(payload)


def test_board_bbox_exceeding_image_width_is_rejected() -> None:
    payload = _payload()
    payload["board"]["bbox"]["x"] = 30
    payload["board"]["bbox"]["width"] = 90

    with pytest.raises(ValidationError, match="board.bbox exceeds image width"):
        MotherboardAnalysisResponse.model_validate(payload)


def test_board_bbox_exceeding_image_height_is_rejected() -> None:
    payload = _payload()
    payload["board"]["bbox"]["y"] = 30
    payload["board"]["bbox"]["height"] = 90

    with pytest.raises(ValidationError, match="board.bbox exceeds image height"):
        MotherboardAnalysisResponse.model_validate(payload)


def test_component_bbox_outside_image_is_rejected() -> None:
    payload = _payload()
    payload["components"][0]["bbox"]["x"] = 95
    payload["components"][0]["bbox"]["width"] = 10

    with pytest.raises(
        ValidationError,
        match=r"components\[0\]\.bbox exceeds image width",
    ):
        MotherboardAnalysisResponse.model_validate(payload)


def test_unknown_arbitrary_component_type_is_rejected() -> None:
    payload = _payload()
    payload["components"][0]["type"] = "gpu_slot"

    with pytest.raises(ValidationError):
        MotherboardAnalysisResponse.model_validate(payload)


def _payload():
    return {
        "image": {"width": 100, "height": 100},
        "board": {
            "label": "motherboard",
            "bbox": {"x": 10, "y": 10, "width": 80, "height": 80},
        },
        "components": [
            {
                "id": "cpu_socket_1",
                "type": "cpu_socket",
                "label": "Socket do processador",
                "description": "Area onde o processador e instalado.",
                "bbox": {"x": 20, "y": 20, "width": 20, "height": 20},
                "shape": "box",
                "estimatedHeight": 0.18,
                "confidence": 0.94,
            }
        ],
    }
