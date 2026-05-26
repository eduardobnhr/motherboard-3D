"""Official Phase 1 data contract for motherboard image analysis.

These schemas define the JSON exchanged between the FastAPI backend and the
frontend 3D renderer. They intentionally do not include any AI integration
details; services and routes should import these models when they are added.
"""

from typing import Literal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# Component categories currently expected by the frontend. The component
# ``type`` field remains a string so the contract can accept future categories
# without a backend schema migration.
class ComponentType(StrEnum):
    """Closed Phase 1 component categories accepted by the 3D viewer."""

    CPU_SOCKET = "cpu_socket"
    RAM_SLOT = "ram_slot"
    PCI_SLOT = "pci_slot"
    CHIPSET = "chipset"
    VRM = "vrm"
    CAPACITOR = "capacitor"
    CONNECTOR = "connector"
    HEATSINK = "heatsink"
    SATA_PORT = "sata_port"
    M2_SLOT = "m2_slot"
    POWER_CONNECTOR = "power_connector"
    UNKNOWN = "unknown"


KNOWN_COMPONENT_TYPES = tuple(component_type.value for component_type in ComponentType)


ComponentShape = Literal["box", "cylinder", "flat"]


class ContractModel(BaseModel):
    """Base model for strict JSON contracts exchanged with the frontend."""

    model_config = ConfigDict(extra="forbid")


class ImageInfo(ContractModel):
    """Pixel dimensions of the uploaded image analyzed by the backend."""

    width: int = Field(..., gt=0, description="Image width in pixels.")
    height: int = Field(..., gt=0, description="Image height in pixels.")


class BoundingBox2D(ContractModel):
    """2D rectangle in image pixel coordinates, measured from the top-left."""

    x: float = Field(..., ge=0, description="Left coordinate in pixels.")
    y: float = Field(..., ge=0, description="Top coordinate in pixels.")
    width: float = Field(..., gt=0, description="Bounding box width in pixels.")
    height: float = Field(..., gt=0, description="Bounding box height in pixels.")


class BoardDetection(ContractModel):
    """Detected motherboard area used as the base plane for the 3D scene."""

    label: str = Field(
        "motherboard",
        description="Human-readable board label, usually 'motherboard'.",
    )
    bbox: BoundingBox2D = Field(
        ...,
        description="Board bounds inside the original image.",
    )


class ComponentDetection(ContractModel):
    """Detected hardware component that the frontend renders as 3D geometry."""

    id: str = Field(
        ...,
        min_length=1,
        description="Stable unique identifier for this detected component.",
        examples=["cpu_socket_1"],
    )
    type: ComponentType = Field(
        ...,
        description=(
            "Closed Phase 1 component category. Allowed values: "
            + ", ".join(KNOWN_COMPONENT_TYPES)
            + "."
        ),
        examples=["cpu_socket"],
    )
    label: str = Field(
        ...,
        min_length=1,
        description="Display name shown in the 3D UI and details panel.",
        examples=["Socket do processador"],
    )
    description: str = Field(
        "",
        description="Short explanation of what the component is or does.",
        examples=["Area onde o processador e instalado"],
    )
    bbox: BoundingBox2D = Field(
        ...,
        description="Component bounds inside the original image.",
    )
    shape: ComponentShape = Field(
        "box",
        description="Initial 3D primitive used by the frontend renderer.",
        examples=["box"],
    )
    estimatedHeight: float = Field(
        0.1,
        ge=0,
        description="Approximate rendered height in normalized 3D scene units.",
        examples=[0.18],
    )
    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Model confidence score from 0.0 to 1.0.",
        examples=[0.94],
    )

    @field_validator("id", "type", "label")
    @classmethod
    def normalize_required_text(cls, value: str | ComponentType) -> str | ComponentType:
        """Trim required strings and reject values that become empty."""

        if isinstance(value, ComponentType):
            return value

        normalized = value.strip()
        if not normalized:
            raise ValueError("Value cannot be empty.")
        return normalized

    @field_validator("type")
    @classmethod
    def normalize_component_type(cls, value: str | ComponentType) -> ComponentType:
        """Normalize known categories and reject arbitrary component types."""

        if isinstance(value, ComponentType):
            return value

        return ComponentType(value.strip().lower())


class MotherboardAnalysisRequest(ContractModel):
    """Metadata request body for future analysis endpoints.

    Image bytes will normally be sent through multipart upload in FastAPI. This
    model captures optional structured request metadata that can accompany the
    upload without changing the official response contract.
    """

    filename: str | None = Field(
        None,
        description="Original uploaded image filename, when available.",
    )
    promptHint: str | None = Field(
        None,
        description="Optional user hint to guide the visual analysis.",
    )


class MotherboardAnalysisResponse(ContractModel):
    """Structured result consumed by the frontend 3D scene."""

    image: ImageInfo = Field(..., description="Analyzed image dimensions.")
    board: BoardDetection = Field(..., description="Detected motherboard bounds.")
    components: list[ComponentDetection] = Field(
        default_factory=list,
        description="Detected motherboard components to render in 3D.",
    )

    @model_validator(mode="after")
    def validate_bboxes_inside_image(self) -> "MotherboardAnalysisResponse":
        """Ensure board and component bounding boxes fit inside the image."""

        _ensure_bbox_inside_image(
            self.board.bbox,
            self.image,
            "board.bbox",
        )

        for index, component in enumerate(self.components):
            _ensure_bbox_inside_image(
                component.bbox,
                self.image,
                f"components[{index}].bbox",
            )

        return self


def _ensure_bbox_inside_image(
    bbox: BoundingBox2D,
    image: ImageInfo,
    field_name: str,
) -> None:
    if bbox.x + bbox.width > image.width:
        raise ValueError(
            f"{field_name} exceeds image width: "
            f"x + width must be <= {image.width}."
        )

    if bbox.y + bbox.height > image.height:
        raise ValueError(
            f"{field_name} exceeds image height: "
            f"y + height must be <= {image.height}."
        )
