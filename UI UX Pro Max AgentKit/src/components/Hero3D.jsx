import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Environment, ContactShadows } from '@react-three/drei';

function FloatingShapes() {
  const group = useRef();
  
  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    group.current.rotation.y = Math.sin(t / 4) / 2;
    group.current.rotation.x = Math.cos(t / 4) / 2;
  });

  return (
    <group ref={group}>
      <Float speed={2} rotationIntensity={1.5} floatIntensity={2}>
        <mesh position={[-1, 0.5, 0]} castShadow>
          <torusKnotGeometry args={[0.5, 0.15, 128, 32]} />
          <meshStandardMaterial color="#7C3AED" roughness={0.2} metalness={0.8} />
        </mesh>
      </Float>

      <Float speed={1.5} rotationIntensity={2} floatIntensity={1.5}>
        <mesh position={[1.2, -0.5, -1]} castShadow>
          <octahedronGeometry args={[0.6]} />
          <meshStandardMaterial color="#EC4899" roughness={0.3} metalness={0.7} />
        </mesh>
      </Float>

      <Float speed={2.5} rotationIntensity={1} floatIntensity={1}>
        <mesh position={[0.5, 1.2, -2]} castShadow>
          <sphereGeometry args={[0.4, 32, 32]} />
          <meshStandardMaterial color="#6366F1" roughness={0.1} metalness={0.9} />
        </mesh>
      </Float>
    </group>
  );
}

export default function Hero3D({ theme = 'dark' }) {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none opacity-60">
      <Canvas camera={{ position: [0, 0, 4], fov: 45 }}>
        <ambientLight intensity={theme === 'dark' ? 0.5 : 0.8} />
        <directionalLight position={[10, 10, 5]} intensity={theme === 'dark' ? 1 : 1.5} />
        <Environment preset={theme === 'dark' ? 'city' : 'studio'} />
        <FloatingShapes />
        <ContactShadows position={[0, -2, 0]} opacity={theme === 'dark' ? 0.4 : 0.15} scale={20} blur={2} far={4.5} />
      </Canvas>
    </div>
  );
}
