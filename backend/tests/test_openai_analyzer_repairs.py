from app.services.openai_motherboard_analyzer import _parse_and_validate_response
from app.utils.image_validation import ValidatedImage


def test_unknown_component_type_is_repaired_before_final_validation() -> None:
    response = _parse_and_validate_response(
        """
        {
          "image": {"width": 100, "height": 100},
          "board": {
            "label": "motherboard",
            "bbox": {"x": 0, "y": 0, "width": 100, "height": 100}
          },
          "components": [
            {
              "id": "component_1",
              "type": "gpu_slot",
              "label": "Componente desconhecido",
              "description": "Componente visivel nao classificado.",
              "bbox": {"x": 10, "y": 10, "width": 20, "height": 20},
              "shape": "box",
              "estimatedHeight": 0.1,
              "confidence": 0.4
            }
          ]
        }
        """,
        ValidatedImage(
            filename="board.png",
            content_type="image/png",
            data=b"image-bytes",
            width=100,
            height=100,
        ),
    )

    assert response.components[0].type == "unknown"
