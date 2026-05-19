/**
 * Official Phase 1 data contract for motherboard image analysis.
 *
 * These types mirror the backend Pydantic schemas in
 * `backend/app/schemas/analysis.py` and describe the JSON consumed by the
 * simplified 3D renderer.
 */

/**
 * Pixel dimensions of the uploaded image analyzed by the backend.
 */
export interface ImageInfo {
  /** Image width in pixels. */
  width: number;
  /** Image height in pixels. */
  height: number;
}

/**
 * 2D rectangle in image pixel coordinates, measured from the top-left.
 */
export interface BoundingBox2D {
  /** Left coordinate in pixels. */
  x: number;
  /** Top coordinate in pixels. */
  y: number;
  /** Bounding box width in pixels. */
  width: number;
  /** Bounding box height in pixels. */
  height: number;
}

/**
 * Detected motherboard area used as the base plane for the 3D scene.
 */
export interface BoardDetection {
  /** Human-readable board label, usually "motherboard". */
  label: string;
  /** Board bounds inside the original image. */
  bbox: BoundingBox2D;
}

/**
 * Initial 3D primitive supported by the frontend renderer.
 */
export type ComponentShape = "box" | "cylinder" | "flat";

/**
 * Component categories currently expected by the frontend.
 */
export type KnownComponentType =
  | "cpu_socket"
  | "ram_slot"
  | "pci_slot"
  | "chipset"
  | "vrm"
  | "capacitor"
  | "connector"
  | "heatsink"
  | "sata_port"
  | "m2_slot"
  | "power_connector"
  | "unknown";

/**
 * Extensible component category. Known values are listed above, while future
 * backend categories can still be represented as strings.
 */
export type ComponentType = KnownComponentType | (string & {});

/**
 * Detected hardware component that the frontend renders as 3D geometry.
 */
export interface ComponentDetection {
  /** Stable unique identifier for this detected component. */
  id: string;
  /** Extensible component category, such as "cpu_socket" or "ram_slot". */
  type: ComponentType;
  /** Display name shown in the 3D UI and details panel. */
  label: string;
  /** Short explanation of what the component is or does. */
  description: string;
  /** Component bounds inside the original image. */
  bbox: BoundingBox2D;
  /** Initial 3D primitive used by the frontend renderer. */
  shape: ComponentShape;
  /** Approximate rendered height in normalized 3D scene units. */
  estimatedHeight: number;
  /** Model confidence score from 0.0 to 1.0. */
  confidence: number;
}

/**
 * Metadata request body for future analysis endpoints.
 *
 * Image bytes will normally be sent through multipart upload. This interface
 * captures optional structured metadata that can accompany the upload without
 * changing the official response contract.
 */
export interface MotherboardAnalysisRequest {
  /** Original uploaded image filename, when available. */
  filename?: string | null;
  /** Optional user hint to guide the visual analysis. */
  promptHint?: string | null;
}

/**
 * Structured result consumed by the frontend 3D scene.
 */
export interface MotherboardAnalysisResponse {
  /** Analyzed image dimensions. */
  image: ImageInfo;
  /** Detected motherboard bounds. */
  board: BoardDetection;
  /** Detected motherboard components to render in 3D. */
  components: ComponentDetection[];
}

