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
  const color = useMemo(() => getComponentColor(component.type), [component.type]);
  const emissive = isHovered || isSelected ? "#ffffff" : "#000000";
  const scale: [number, number, number] =
    isSelected ? [1.04, 1.12, 1.04] : [1, 1, 1];

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
          color={color}
          emissive={emissive}
          emissiveIntensity={isHovered || isSelected ? 0.16 : 0}
          metalness={0.12}
          roughness={0.58}
        />
      </mesh>

      {(isHovered || isSelected) && (
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

function getComponentColor(type: string): THREE.ColorRepresentation {
  const colors: Record<string, string> = {
    cpu_socket: "#d6d1c4",
    ram_slot: "#415f96",
    pci_slot: "#2f3747",
    chipset: "#6f4d91",
    vrm: "#5f6872",
    capacitor: "#997c39",
    connector: "#b7b34a",
    heatsink: "#7f8c8d",
    sata_port: "#d86d3f",
    m2_slot: "#3f7a70",
    power_connector: "#d1d5d8",
    unknown: "#8a8f95",
  };

  return colors[type] ?? colors.unknown;
}
