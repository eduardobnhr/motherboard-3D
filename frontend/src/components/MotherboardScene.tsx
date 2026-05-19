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

  return (
    <div className="scene-shell">
      <Canvas
        camera={{ position: [0, 5.8, 7.6], fov: 42 }}
        shadows
        gl={{ antialias: true }}
      >
        <color attach="background" args={["#edf1ed"]} />
        <Suspense fallback={null}>
          <SceneLights />
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
            maxDistance={14}
            maxPolarAngle={Math.PI / 2.15}
            minDistance={4}
            target={[0, 0, 0]}
          />
        </Suspense>
      </Canvas>
    </div>
  );
}

