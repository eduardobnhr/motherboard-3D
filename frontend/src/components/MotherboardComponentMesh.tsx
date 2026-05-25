import { Html, useCursor } from "@react-three/drei";
import type { ThreeEvent } from "@react-three/fiber";
import { useMemo, useState } from "react";
import * as THREE from "three";

import type { ComponentDetection } from "../types/analysis";
import type { MappedComponent } from "../utils/sceneMapping";

interface MotherboardComponentMeshProps {
  mappedComponent: MappedComponent;
  isSelected: boolean;
  onSelectComponent: (component: ComponentDetection) => void;
}

export function MotherboardComponentMesh({
  mappedComponent,
  isSelected,
  onSelectComponent,
}: MotherboardComponentMeshProps) {
  const [isHovered, setIsHovered] = useState(false);
  const { component, position, size } = mappedComponent;
  const material = useMemo(
    () => getComponentMaterial(component.type),
    [component.type],
  );
  const emissive = isSelected ? "#f7d354" : isHovered ? "#ffffff" : "#000000";
  const scale: [number, number, number] =
    isSelected ? [1.08, 1.2, 1.08] : isHovered ? [1.03, 1.06, 1.03] : [1, 1, 1];

  useCursor(isHovered);

  function handleClick(event: ThreeEvent<MouseEvent>) {
    event.stopPropagation();
    onSelectComponent(component);
  }

  function handlePointerOver(event: ThreeEvent<PointerEvent>) {
    event.stopPropagation();
    setIsHovered(true);
  }

  function handlePointerOut(event: ThreeEvent<PointerEvent>) {
    event.stopPropagation();
    setIsHovered(false);
  }

  return (
    <group position={position} scale={scale}>
      <mesh
        castShadow
        onClick={handleClick}
        onPointerOut={handlePointerOut}
        onPointerOver={handlePointerOver}
      >
        <ComponentGeometry component={component} size={size} />
        <meshStandardMaterial
          color={material.color}
          emissive={emissive}
          emissiveIntensity={isSelected ? 0.35 : isHovered ? 0.14 : 0}
          metalness={material.metalness}
          roughness={material.roughness}
        />
      </mesh>

      {isSelected && (
        <mesh position={[0, -size[1] / 2 - 0.004, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry
            args={[
              Math.max(size[0], size[2]) * 0.58,
              Math.max(size[0], size[2]) * 0.68,
              48,
            ]}
          />
          <meshBasicMaterial color="#f7d354" transparent opacity={0.88} />
        </mesh>
      )}

      {isHovered && (
        <Html center distanceFactor={8} position={[0, size[1] / 2 + 0.22, 0]}>
          <div className="component-tooltip">{component.label}</div>
        </Html>
      )}
    </group>
  );
}

function ComponentGeometry({
  component,
  size,
}: {
  component: ComponentDetection;
  size: [number, number, number];
}) {
  if (component.shape === "cylinder") {
    const radius = Math.max(size[0], size[2]) / 2;
    return <cylinderGeometry args={[radius, radius, size[1], 32]} />;
  }

  return <boxGeometry args={size} />;
}

function getComponentMaterial(type: string): {
  color: THREE.ColorRepresentation;
  metalness: number;
  roughness: number;
} {
  const materials: Record<
    string,
    { color: string; metalness: number; roughness: number }
  > = {
    cpu_socket: { color: "#d8d2c2", metalness: 0.08, roughness: 0.5 },
    ram_slot: { color: "#355a9a", metalness: 0.05, roughness: 0.62 },
    pci_slot: { color: "#252d3a", metalness: 0.04, roughness: 0.7 },
    chipset: { color: "#68468d", metalness: 0.1, roughness: 0.48 },
    vrm: { color: "#59636f", metalness: 0.18, roughness: 0.42 },
    capacitor: { color: "#9f7d32", metalness: 0.24, roughness: 0.38 },
    connector: { color: "#c6be55", metalness: 0.08, roughness: 0.56 },
    heatsink: { color: "#8d9a9c", metalness: 0.45, roughness: 0.32 },
    sata_port: { color: "#d96a3d", metalness: 0.06, roughness: 0.58 },
    m2_slot: { color: "#36796d", metalness: 0.06, roughness: 0.62 },
    power_connector: { color: "#d7dce0", metalness: 0.08, roughness: 0.45 },
    unknown: { color: "#8a8f95", metalness: 0.05, roughness: 0.6 },
  };

  return materials[type] ?? materials.unknown;
}
