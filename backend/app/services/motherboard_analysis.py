"""Motherboard image analysis service."""

from app.schemas.analysis import (
    BoardDetection,
    BoundingBox2D,
    ComponentDetection,
    ImageInfo,
    MotherboardAnalysisResponse,
)
from app.services.openai_motherboard_analyzer import OpenAIMotherboardAnalyzer
from app.utils.image_validation import ValidatedImage


class MotherboardAnalysisService:
    """Analyze motherboard images and return the official Phase 1 contract."""

    def __init__(
        self,
        analyzer: OpenAIMotherboardAnalyzer | None = None,
        use_mock_analyzer: bool = False,
    ) -> None:
        self.analyzer = analyzer
        self.use_mock_analyzer = use_mock_analyzer

    async def analyze(self, image: ValidatedImage) -> MotherboardAnalysisResponse:
        """Analyze an uploaded image with OpenAI or a development mock."""

        if self.use_mock_analyzer or self.analyzer is None:
            return build_mock_analysis_response(image.width, image.height)

        return await self.analyzer.analyze(image)


def build_mock_analysis_response(
    image_width: int,
    image_height: int,
) -> MotherboardAnalysisResponse:
    """Build stable mock detections scaled to the uploaded image dimensions."""

    board_x = image_width * 0.07
    board_y = image_height * 0.08
    board_width = image_width * 0.86
    board_height = image_height * 0.84

    def box(
        rel_x: float,
        rel_y: float,
        rel_width: float,
        rel_height: float,
    ) -> BoundingBox2D:
        return BoundingBox2D(
            x=board_x + board_width * rel_x,
            y=board_y + board_height * rel_y,
            width=board_width * rel_width,
            height=board_height * rel_height,
        )

    return MotherboardAnalysisResponse(
        image=ImageInfo(width=image_width, height=image_height),
        board=BoardDetection(
            label="motherboard",
            bbox=BoundingBox2D(
                x=board_x,
                y=board_y,
                width=board_width,
                height=board_height,
            ),
        ),
        components=[
            ComponentDetection(
                id="cpu_socket_1",
                type="cpu_socket",
                label="Socket do processador",
                description="Area onde o processador e instalado.",
                bbox=box(0.38, 0.30, 0.16, 0.18),
                shape="box",
                estimatedHeight=0.18,
                confidence=0.94,
            ),
            ComponentDetection(
                id="ram_slot_1",
                type="ram_slot",
                label="Slot de memoria RAM 1",
                description="Conector alongado para modulo de memoria RAM.",
                bbox=box(0.60, 0.20, 0.045, 0.42),
                shape="box",
                estimatedHeight=0.08,
                confidence=0.91,
            ),
            ComponentDetection(
                id="ram_slot_2",
                type="ram_slot",
                label="Slot de memoria RAM 2",
                description="Segundo conector alongado para modulo de memoria RAM.",
                bbox=box(0.66, 0.20, 0.045, 0.42),
                shape="box",
                estimatedHeight=0.08,
                confidence=0.90,
            ),
            ComponentDetection(
                id="pci_slot_1",
                type="pci_slot",
                label="Slot PCI Express",
                description="Conector de expansao para placa de video ou perifericos.",
                bbox=box(0.24, 0.66, 0.46, 0.07),
                shape="box",
                estimatedHeight=0.07,
                confidence=0.88,
            ),
            ComponentDetection(
                id="chipset_1",
                type="chipset",
                label="Chipset",
                description="Controlador principal de comunicacao da placa-mae.",
                bbox=box(0.52, 0.56, 0.13, 0.13),
                shape="box",
                estimatedHeight=0.14,
                confidence=0.86,
            ),
            ComponentDetection(
                id="power_connector_1",
                type="power_connector",
                label="Conector de alimentacao",
                description="Conector principal de energia da placa-mae.",
                bbox=box(0.79, 0.27, 0.08, 0.25),
                shape="box",
                estimatedHeight=0.12,
                confidence=0.89,
            ),
        ],
    )
