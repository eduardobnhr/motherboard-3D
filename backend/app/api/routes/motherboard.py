"""Motherboard analysis API routes."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.config import Settings, get_settings
from app.schemas.analysis import MotherboardAnalysisResponse
from app.services.motherboard_analysis import MotherboardAnalysisService
from app.utils.image_validation import ImageValidationError, validate_uploaded_image


router = APIRouter(prefix="/motherboard", tags=["motherboard"])


def get_analysis_service() -> MotherboardAnalysisService:
    """Provide the motherboard analysis service."""

    return MotherboardAnalysisService()


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
            settings.max_image_upload_bytes,
        )
        return await service.analyze(validated_image)
    except ImageValidationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    finally:
        await file.close()

