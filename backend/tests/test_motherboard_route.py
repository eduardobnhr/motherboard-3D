from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.core.dependencies import get_motherboard_analysis_service
from app.main import app
from app.services.mock_motherboard_analyzer import MockMotherboardAnalyzer
from app.services.motherboard_analysis import MotherboardAnalysisService


def test_motherboard_analyze_uses_overridden_service_dependency() -> None:
    app.dependency_overrides[get_motherboard_analysis_service] = (
        _override_analysis_service
    )

    try:
        client = TestClient(app)
        response = client.post(
            "/api/motherboard/analyze",
            files={
                "file": (
                    "board.png",
                    _png_bytes(32, 24),
                    "image/png",
                )
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["image"] == {"width": 32, "height": 24}
    assert payload["board"]["label"] == "motherboard"
    assert payload["components"][0]["type"] == "cpu_socket"


def _override_analysis_service() -> MotherboardAnalysisService:
    return MotherboardAnalysisService(analyzer=MockMotherboardAnalyzer())


def _png_bytes(width: int, height: int) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (width, height), color=(20, 80, 60)).save(
        buffer,
        format="PNG",
    )
    return buffer.getvalue()

