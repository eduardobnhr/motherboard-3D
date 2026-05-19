"""OpenAI-backed motherboard image analyzer."""

import base64
import json
from typing import Any

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI
from pydantic import ValidationError

from app.schemas.analysis import MotherboardAnalysisResponse
from app.utils.image_validation import ValidatedImage


ALLOWED_COMPONENT_TYPES = [
    "cpu_socket",
    "ram_slot",
    "pci_slot",
    "chipset",
    "vrm",
    "capacitor",
    "connector",
    "heatsink",
    "sata_port",
    "m2_slot",
    "power_connector",
    "unknown",
]


MOTHERBOARD_ANALYSIS_PROMPT = """You are a careful computer-vision analyst for PC motherboard images.

Return ONLY valid JSON matching the provided schema. Do not include markdown, comments, explanations, or extra keys.

Rules:
- Analyze only components that are clearly visible in the image.
- Do not invent or infer hidden components.
- Fill image.width and image.height using the exact image dimensions supplied by the user.
- Detect the motherboard board area and provide board.bbox in original image pixel coordinates.
- Detect the main visible motherboard components, prioritizing:
  cpu socket, RAM slots, PCI Express slots, chipset, VRM area, capacitors, heatsinks,
  power connectors, SATA ports, M.2 slots, and other relevant connectors.
- Every bbox must use original image pixels with origin at the top-left corner:
  x, y, width, height.
- Keep bbox values inside the image bounds.
- Use type only from this allowed list:
  cpu_socket, ram_slot, pci_slot, chipset, vrm, capacitor, connector, heatsink,
  sata_port, m2_slot, power_connector, unknown.
- Use shape as one of: box, cylinder, flat.
- Use estimatedHeight as a normalized visual height for a simplified 3D viewer:
  flat printed areas and slots: 0.03-0.08;
  sockets/connectors/chipsets: 0.08-0.18;
  capacitors/heatsinks/tall connectors: 0.14-0.35.
- Use confidence between 0 and 1.
- Use stable ids like cpu_socket_1, ram_slot_1, pci_slot_1.
- Prefer concise Portuguese labels and descriptions for UI display.
- If a category is uncertain but visible, use type "unknown" and a lower confidence.
"""


MOTHERBOARD_ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["image", "board", "components"],
    "properties": {
        "image": {
            "type": "object",
            "additionalProperties": False,
            "required": ["width", "height"],
            "properties": {
                "width": {"type": "integer", "minimum": 1},
                "height": {"type": "integer", "minimum": 1},
            },
        },
        "board": {
            "type": "object",
            "additionalProperties": False,
            "required": ["label", "bbox"],
            "properties": {
                "label": {"type": "string"},
                "bbox": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["x", "y", "width", "height"],
                    "properties": {
                        "x": {"type": "number", "minimum": 0},
                        "y": {"type": "number", "minimum": 0},
                        "width": {"type": "number", "minimum": 1},
                        "height": {"type": "number", "minimum": 1},
                    },
                },
            },
        },
        "components": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "id",
                    "type",
                    "label",
                    "description",
                    "bbox",
                    "shape",
                    "estimatedHeight",
                    "confidence",
                ],
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string", "enum": ALLOWED_COMPONENT_TYPES},
                    "label": {"type": "string"},
                    "description": {"type": "string"},
                    "bbox": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["x", "y", "width", "height"],
                        "properties": {
                            "x": {"type": "number", "minimum": 0},
                            "y": {"type": "number", "minimum": 0},
                            "width": {"type": "number", "minimum": 1},
                            "height": {"type": "number", "minimum": 1},
                        },
                    },
                    "shape": {
                        "type": "string",
                        "enum": ["box", "cylinder", "flat"],
                    },
                    "estimatedHeight": {"type": "number", "minimum": 0},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
        },
    },
}


class MotherboardAnalysisError(RuntimeError):
    """Domain error raised when image analysis cannot produce a valid result."""


class OpenAIMotherboardAnalyzer:
    """Analyze a motherboard image using OpenAI multimodal models."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout_seconds)

    async def analyze(self, image: ValidatedImage) -> MotherboardAnalysisResponse:
        """Return a validated motherboard analysis for the uploaded image."""

        try:
            response = await self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "input_text",
                                "text": MOTHERBOARD_ANALYSIS_PROMPT,
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "Analyze this motherboard image. "
                                    f"The trusted image dimensions are "
                                    f"{image.width}x{image.height} pixels."
                                ),
                            },
                            {
                                "type": "input_image",
                                "image_url": _to_data_url(image),
                            },
                        ],
                    },
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "motherboard_analysis_response",
                        "strict": True,
                        "schema": MOTHERBOARD_ANALYSIS_SCHEMA,
                    }
                },
            )
        except (APIConnectionError, APITimeoutError) as exc:
            raise MotherboardAnalysisError(
                "Could not connect to the OpenAI analysis service."
            ) from exc
        except APIError as exc:
            raise MotherboardAnalysisError(
                "OpenAI analysis service returned an error."
            ) from exc

        return _parse_and_validate_response(response.output_text, image)


def _to_data_url(image: ValidatedImage) -> str:
    encoded = base64.b64encode(image.data).decode("ascii")
    return f"data:{image.content_type};base64,{encoded}"


def _parse_and_validate_response(
    output_text: str,
    image: ValidatedImage,
) -> MotherboardAnalysisResponse:
    try:
        raw_payload = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise MotherboardAnalysisError(
            "OpenAI returned invalid JSON for the motherboard analysis."
        ) from exc

    repaired_payload = _apply_safe_repairs(raw_payload, image)

    try:
        return MotherboardAnalysisResponse.model_validate(repaired_payload)
    except ValidationError as exc:
        raise MotherboardAnalysisError(
            "OpenAI returned JSON that does not match the analysis contract."
        ) from exc


def _apply_safe_repairs(payload: Any, image: ValidatedImage) -> Any:
    """Apply deterministic repairs that do not invent visual components."""

    if not isinstance(payload, dict):
        return payload

    payload["image"] = {"width": image.width, "height": image.height}

    components = payload.get("components")
    if isinstance(components, list):
        for component in components:
            if not isinstance(component, dict):
                continue

            if component.get("type") not in ALLOWED_COMPONENT_TYPES:
                component["type"] = "unknown"

            bbox = component.get("bbox")
            if isinstance(bbox, dict):
                _clamp_bbox(bbox, image.width, image.height)

    board = payload.get("board")
    if isinstance(board, dict) and isinstance(board.get("bbox"), dict):
        _clamp_bbox(board["bbox"], image.width, image.height)

    return payload


def _clamp_bbox(bbox: dict[str, Any], image_width: int, image_height: int) -> None:
    x = _clamp_number(bbox.get("x"), 0, image_width - 1)
    y = _clamp_number(bbox.get("y"), 0, image_height - 1)
    width = _clamp_number(bbox.get("width"), 1, image_width - x)
    height = _clamp_number(bbox.get("height"), 1, image_height - y)

    bbox["x"] = x
    bbox["y"] = y
    bbox["width"] = width
    bbox["height"] = height


def _clamp_number(value: Any, minimum: float, maximum: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return minimum

    return min(max(number, minimum), maximum)
