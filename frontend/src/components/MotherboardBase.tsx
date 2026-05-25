import type { SceneDimensions } from "../utils/sceneMapping";

interface MotherboardBaseProps {
  dimensions: SceneDimensions;
}

export function MotherboardBase({ dimensions }: MotherboardBaseProps) {
  return (
    <group>
      <mesh position={[0, 0, 0]} receiveShadow>
        <boxGeometry
          args={[
            dimensions.boardWidth,
            dimensions.boardThickness,
            dimensions.boardDepth,
          ]}
        />
        <meshStandardMaterial color="#214f3b" roughness={0.82} metalness={0.04} />
      </mesh>

      <gridHelper
        args={[
          Math.max(dimensions.boardWidth, dimensions.boardDepth),
          20,
          "#4f876b",
          "#2c654b",
        ]}
        position={[0, dimensions.boardThickness / 2 + 0.003, 0]}
      />
    </group>
  );
}
