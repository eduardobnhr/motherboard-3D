"""FastAPI dependency factories for application services."""

from functools import lru_cache

from fastapi import Depends, HTTPException

from app.core.config import Settings, get_settings
from app.services.mock_motherboard_analyzer import MockMotherboardAnalyzer
from app.services.motherboard_analysis import MotherboardAnalysisService
from app.services.openai_motherboard_analyzer import OpenAIMotherboardAnalyzer


def get_motherboard_analysis_service(
    settings: Settings = Depends(get_settings),
) -> MotherboardAnalysisService:
    """Return the configured motherboard analysis service."""

    return _build_motherboard_analysis_service(
        use_mock_analyzer=settings.use_mock_analyzer,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
        openai_timeout_seconds=settings.openai_timeout_seconds,
    )


@lru_cache
def _build_motherboard_analysis_service(
    use_mock_analyzer: bool,
    openai_api_key: str | None,
    openai_model: str,
    openai_timeout_seconds: float,
) -> MotherboardAnalysisService:
    """Build and cache the analysis service and provider client."""

    if use_mock_analyzer:
        return MotherboardAnalysisService(analyzer=MockMotherboardAnalyzer())

    if not openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured.",
        )

    return MotherboardAnalysisService(
        analyzer=OpenAIMotherboardAnalyzer(
            api_key=openai_api_key,
            model=openai_model,
            timeout_seconds=openai_timeout_seconds,
        )
    )

