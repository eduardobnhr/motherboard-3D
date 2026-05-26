import pytest

from app.services.errors import MotherboardAnalysisError
from app.services.openai_motherboard_analyzer import (
    OpenAIMotherboardAnalyzer,
    _parse_and_validate_response,
)
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


@pytest.mark.anyio
async def test_openai_transient_failure_retries_and_then_succeeds(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.openai_motherboard_analyzer.asyncio.sleep",
        _skip_sleep,
    )
    analyzer = OpenAIMotherboardAnalyzer(
        api_key="test-key",
        model="gpt-4o",
        timeout_seconds=1,
    )
    analyzer.client = _FakeClient(
        [
            TimeoutError("temporary timeout"),
            _FakeResponse(_valid_json_response()),
        ]
    )

    response = await analyzer.analyze(_validated_image())

    assert response.components[0].type == "cpu_socket"
    assert analyzer.client.responses.calls == 2


@pytest.mark.anyio
async def test_invalid_json_is_not_retried(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.openai_motherboard_analyzer.asyncio.sleep",
        _skip_sleep,
    )
    analyzer = OpenAIMotherboardAnalyzer(
        api_key="test-key",
        model="gpt-4o",
        timeout_seconds=1,
    )
    analyzer.client = _FakeClient([_FakeResponse("not-json")])

    with pytest.raises(MotherboardAnalysisError):
        await analyzer.analyze(_validated_image())

    assert analyzer.client.responses.calls == 1


async def _skip_sleep(_: float) -> None:
    return None


class _FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class _FakeClient:
    def __init__(self, outcomes) -> None:
        self.responses = _FakeResponses(outcomes)


class _FakeResponses:
    def __init__(self, outcomes) -> None:
        self.outcomes = list(outcomes)
        self.calls = 0

    async def create(self, **kwargs):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _validated_image() -> ValidatedImage:
    return ValidatedImage(
        filename="board.png",
        content_type="image/png",
        data=b"image-bytes",
        width=100,
        height=100,
    )


def _valid_json_response() -> str:
    return """
    {
      "image": {"width": 100, "height": 100},
      "board": {
        "label": "motherboard",
        "bbox": {"x": 0, "y": 0, "width": 100, "height": 100}
      },
      "components": [
        {
          "id": "cpu_socket_1",
          "type": "cpu_socket",
          "label": "Socket do processador",
          "description": "Area onde o processador e instalado.",
          "bbox": {"x": 10, "y": 10, "width": 20, "height": 20},
          "shape": "box",
          "estimatedHeight": 0.18,
          "confidence": 0.94
        }
      ]
    }
    """
