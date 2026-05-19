export function SceneLights() {
  return (
    <>
      <ambientLight intensity={0.65} />
      <directionalLight position={[4, 8, 5]} intensity={1.6} />
      <directionalLight position={[-5, 4, -3]} intensity={0.55} />
    </>
  );
}

