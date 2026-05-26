"""Motherboard image analysis service."""

from app.schemas.analysis import MotherboardAnalysisResponse
from app.services.motherboard_analyzer import MotherboardAnalyzer
from app.utils.image_validation import ValidatedImage


class MotherboardAnalysisService:
    """Analyze motherboard images and return the official Phase 1 contract."""

    def __init__(self, analyzer: MotherboardAnalyzer) -> None:
        self.analyzer = analyzer

    async def analyze(self, image: ValidatedImage) -> MotherboardAnalysisResponse:
        """Analyze an uploaded image using the configured analyzer provider."""

        return await self.analyzer.analyze(image)
