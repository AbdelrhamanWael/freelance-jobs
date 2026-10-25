/**
 * ModelCard3D.jsx
 * ───────────────────────────────────────────────────────────────
 * A compact React Three Fiber canvas embedded within the
 * generation result cards. Shows a rotating 3D preview with
 * studio lighting and a glowing material.
 */

import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { MeshDistortMaterial, MeshWobbleMaterial, Environment } from '@react-three/drei';
import * as THREE from 'three';

const SHAPE_CONFIGS = {
  box: {
    geo: <boxGeometry args={[1.2, 1.2, 1.2]} />,
    color: '#7C3AED',
    distort: 0.15,
    speed: 1,
  },
  sphere: {
    geo: <sphereGeometry args={[0.85, 32, 32]} />,
    color: '#6366F1',
    distort: 0.35,
    speed: 2,
  },
  torus: {
    geo: <torusGeometry args={[0.65, 0.28, 24, 64]} />,
    color: '#EC4899',
    distort: 0.1,
    speed: 1.5,
  },
  icosahedron: {
    geo: <icosahedronGeometry args={[0.9, 1]} />,
    color: '#00D4FF',
    distort: 0.2,
    speed: 1.2,
  },
};

function RotatingMesh({ shape }) {
  const meshRef = useRef();
  const cfg = SHAPE_CONFIGS[shape] || SHAPE_CONFIGS.box;

  useFrame((state, delta) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.y += delta * 0.8;
    meshRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.4) * 0.25;
  });

  return (
    <mesh ref={meshRef} castShadow>
      {cfg.geo}
      <MeshDistortMaterial
        color={cfg.color}
        roughness={0.05}
        metalness={0.9}
        distort={cfg.distort}
        speed={cfg.speed}
        envMapIntensity={2}
      />
    </mesh>
  );
}

/**
 * ModelCard3D
 * @param {string} shape  - 'box' | 'sphere' | 'torus' | 'icosahedron'
 * @param {string} label  - Display name shown below the canvas
 * @param {string} glow   - Tailwind glow class (e.g. 'glow-primary')
 * @param {function} onClick
 */
export default function ModelCard3D({ shape, label, glow, onClick }) {
  const cfg = SHAPE_CONFIGS[shape] || SHAPE_CONFIGS.box;

  return (
    <div
      id={`model-card-${shape}`}
      onClick={onClick}
      className={`
        group relative cursor-pointer rounded-2xl overflow-hidden
        border border-white/10 hover:border-white/25
        bg-black/30 hover:bg-black/50
        transition-all duration-300 hover:-translate-y-1.5
        ${glow}
      `}
    >
      {/* AI Badge */}
      <div className="absolute top-2.5 right-2.5 z-10 flex items-center gap-1 bg-black/50 backdrop-blur-md px-2 py-1 rounded-full border border-white/10 text-[10px] text-white/70">
        <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse inline-block" />
        AI
      </div>

      {/* 3D Canvas */}
      <div className="aspect-square w-full">
        <Canvas
          gl={{ antialias: true, alpha: true }}
          camera={{ position: [0, 0, 3], fov: 45 }}
          shadows
          style={{ background: 'transparent' }}
        >
          <ambientLight intensity={0.4} />
          <spotLight
            position={[4, 4, 4]}
            angle={0.25}
            penumbra={1}
            intensity={3}
            castShadow
            color="#ffffff"
          />
          <pointLight position={[-2, -2, -2]} intensity={1} color={cfg.color} />
          <Environment preset="city" />
          <RotatingMesh shape={shape} />
        </Canvas>
      </div>

      {/* Label */}
      <div className="px-4 py-3 text-center border-t border-white/5">
        <span className="text-sm font-medium text-white/80 group-hover:text-white transition-colors">
          {label}
        </span>
      </div>

      {/* Hover glow overlay */}
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none rounded-2xl"
        style={{
          background: `radial-gradient(circle at center, ${cfg.color}18 0%, transparent 70%)`,
        }}
      />
    </div>
  );
}
