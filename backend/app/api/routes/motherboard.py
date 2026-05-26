"""Motherboard analysis API routes."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.config import Settings, get_settings
from app.schemas.analysis import MotherboardAnalysisResponse
from app.services.motherboard_analysis import MotherboardAnalysisService
from app.services.openai_motherboard_analyzer import (
    MotherboardAnalysisError,
    OpenAIMotherboardAnalyzer,
)
from app.utils.image_validation import ImageValidationError, validate_uploaded_image


router = APIRouter(prefix="/motherboard", tags=["motherboard"])


def get_analysis_service(
    settings: Settings = Depends(get_settings),
) -> MotherboardAnalysisService:
    """Provide the motherboard analysis service."""

    if settings.use_mock_analyzer:
        return MotherboardAnalysisService(use_mock_analyzer=True)

    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured.",
        )

    return MotherboardAnalysisService(
        analyzer=OpenAIMotherboardAnalyzer(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout_seconds=settings.openai_timeout_seconds,
        )
    )


@router.post(
    "/analyze",
    response_model=MotherboardAnalysisResponse,
    summary="Analyze an uploaded motherboard image",
)
async def analyze_motherboard(
    file: UploadFile = File(..., description="PNG, JPG, or JPEG motherboard image."),
    settings: Settings = Depends(get_settings),
    service: MotherboardAnalysisService = Depends(get_analysis_service),
) -> MotherboardAnalysisResponse:
    """Validate an image upload and return a Phase 1 analysis response."""

    try:
        validated_image = await validate_uploaded_image(
            file,
            settings.image_validation_limits,
        )
        return await service.analyze(validated_image)
    except ImageValidationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except MotherboardAnalysisError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        await file.close()
