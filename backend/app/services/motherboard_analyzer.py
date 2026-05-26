"""Analyzer abstractions for motherboard image analysis providers."""

from typing import Protocol

from app.schemas.analysis import MotherboardAnalysisResponse
from app.utils.image_validation import ValidatedImage


class MotherboardAnalyzer(Protocol):
    """Provider interface implemented by OpenAI, mock, or future CV analyzers."""

    async def analyze(self, image: ValidatedImage) -> MotherboardAnalysisResponse:
        """Analyze a validated image and return the Phase 1 response contract."""

