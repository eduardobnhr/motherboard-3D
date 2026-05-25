export function SceneLights() {
  return (
    <>
      <ambientLight intensity={0.72} />
      <directionalLight
        castShadow
        intensity={1.25}
        position={[5, 8, 6]}
        shadow-mapSize-height={1024}
        shadow-mapSize-width={1024}
      />
      <directionalLight position={[-4, 3, -5]} intensity={0.38} />
    </>
  );
}
