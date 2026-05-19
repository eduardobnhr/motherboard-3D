import type {
  BoundingBox2D,
  ComponentDetection,
  MotherboardAnalysisResponse,
} from "../types/analysis";

export interface SceneDimensions {
  boardWidth: number;
  boardDepth: number;
  boardThickness: number;
}

export interface MappedComponent {
  component: ComponentDetection;
  position: [number, number, number];
  size: [number, number, number];
}

const DEFAULT_BOARD_WIDTH = 8;
const DEFAULT_BOARD_THICKNESS = 0.08;
const MIN_COMPONENT_SIZE = 0.08;
const MIN_COMPONENT_HEIGHT = 0.035;

export function getSceneDimensions(
  analysis: MotherboardAnalysisResponse,
): SceneDimensions {
  const boardAspectRatio = analysis.board.bbox.height / analysis.board.bbox.width;

  return {
    boardWidth: DEFAULT_BOARD_WIDTH,
    boardDepth: DEFAULT_BOARD_WIDTH * boardAspectRatio,
    boardThickness: DEFAULT_BOARD_THICKNESS,
  };
}

export function mapComponentToScene(
  component: ComponentDetection,
  boardBbox: BoundingBox2D,
  dimensions: SceneDimensions,
): MappedComponent {
  const relativeCenterX =
    (component.bbox.x + component.bbox.width / 2 - boardBbox.x) / boardBbox.width;
  const relativeCenterY =
    (component.bbox.y + component.bbox.height / 2 - boardBbox.y) /
    boardBbox.height;

  const width = Math.max(
    MIN_COMPONENT_SIZE,
    (component.bbox.width / boardBbox.width) * dimensions.boardWidth,
  );
  const depth = Math.max(
    MIN_COMPONENT_SIZE,
    (component.bbox.height / boardBbox.height) * dimensions.boardDepth,
  );
  const height = getComponentHeight(component);

  return {
    component,
    position: [
      (relativeCenterX - 0.5) * dimensions.boardWidth,
      dimensions.boardThickness / 2 + height / 2,
      (0.5 - relativeCenterY) * dimensions.boardDepth,
    ],
    size: [width, height, depth],
  };
}

export function mapComponentsToScene(
  analysis: MotherboardAnalysisResponse,
  dimensions: SceneDimensions,
): MappedComponent[] {
  return analysis.components.map((component) =>
    mapComponentToScene(component, analysis.board.bbox, dimensions),
  );
}

function getComponentHeight(component: ComponentDetection): number {
  if (component.shape === "flat") {
    return Math.max(MIN_COMPONENT_HEIGHT, component.estimatedHeight * 0.35);
  }

  return Math.max(MIN_COMPONENT_HEIGHT, component.estimatedHeight);
}

