import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Suspense, useMemo } from "react";

import type {
  ComponentDetection,
  MotherboardAnalysisResponse,
} from "../types/analysis";
import {
  getSceneDimensions,
  mapComponentsToScene,
} from "../utils/sceneMapping";
import { MotherboardBase } from "./MotherboardBase";
import { MotherboardComponentMesh } from "./MotherboardComponentMesh";
import { SceneLights } from "./SceneLights";

interface MotherboardSceneProps {
  analysis: MotherboardAnalysisResponse;
  selectedComponentId?: string;
  onSelectComponent: (component: ComponentDetection) => void;
}

export function MotherboardScene({
  analysis,
  selectedComponentId,
  onSelectComponent,
}: MotherboardSceneProps) {
  const dimensions = useMemo(() => getSceneDimensions(analysis), [analysis]);
  const mappedComponents = useMemo(
    () => mapComponentsToScene(analysis, dimensions),
    [analysis, dimensions],
  );
  const cameraDistance = dimensions.fitDistance * 1.18;
  const cameraPosition: [number, number, number] = [
    cameraDistance,
    cameraDistance * 0.82,
    cameraDistance,
  ];

  return (
    <div className="scene-shell">
      <Canvas
        camera={{ position: cameraPosition, fov: 35 }}
        shadows
        gl={{ antialias: true }}
      >
        <color attach="background" args={["#eef2ef"]} />
        <Suspense fallback={null}>
          <SceneLights />
          <gridHelper
            args={[
              Math.max(dimensions.boardWidth, dimensions.boardDepth) * 1.45,
              18,
              "#d7ded8",
              "#e7ece8",
            ]}
            position={[0, -0.055, 0]}
          />
          <group rotation={[0, 0, 0]}>
            <MotherboardBase dimensions={dimensions} />
            {mappedComponents.map((mappedComponent) => (
              <MotherboardComponentMesh
                key={mappedComponent.component.id}
                isSelected={
                  mappedComponent.component.id === selectedComponentId
                }
                mappedComponent={mappedComponent}
                onSelectComponent={onSelectComponent}
              />
            ))}
          </group>
          <OrbitControls
            enableDamping
            dampingFactor={0.08}
            maxDistance={dimensions.fitDistance * 2.4}
            maxPolarAngle={Math.PI / 2.08}
            minDistance={dimensions.fitDistance * 0.55}
            target={[0, 0, 0]}
          />
        </Suspense>
      </Canvas>
    </div>
  );
}
