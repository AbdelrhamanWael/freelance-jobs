/**
 * LogoJourney.jsx
 * ───────────────────────────────────────────────────────────────
 * The 3D hero object that "falls" and journeys through the page
 * as the user scrolls. Uses React Three Fiber + @react-three/drei
 * ScrollControls to animate a compound 3D logo shape.
 *
 * Animation Phases (scroll.offset 0 → 1):
 *  0.00 – 0.25  Hero: centered, large, floating with pulse
 *  0.25 – 0.60  Falling: tumbles to bottom-left corner
 *  0.60 – 0.80  Workspace: rests in corner, slow spin
 *  0.80 – 1.00  Exit: scales to 0, fades out
 */

import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { useScroll, Float, MeshDistortMaterial, Torus } from '@react-three/drei';
import * as THREE from 'three';

// ── Inner animated ring ──────────────────────────────────────────
function Ring({ radius, tube, color, speed, phase }) {
  const ref = useRef();
  useFrame((state) => {
    if (!ref.current) return;
    ref.current.rotation.x = state.clock.elapsedTime * speed + phase;
    ref.current.rotation.z = state.clock.elapsedTime * speed * 0.7 + phase;
  });
  return (
    <Torus ref={ref} args={[radius, tube, 24, 64]}>
      <meshStandardMaterial
        color={color}
        roughness={0.05}
        metalness={1}
        envMapIntensity={3}
      />
    </Torus>
  );
}

// ── Core distorted sphere (the "B" nucleus) ──────────────────────
function Nucleus() {
  const ref = useRef();
  return (
    <mesh ref={ref} castShadow receiveShadow>
      <icosahedronGeometry args={[0.55, 4]} />
      <MeshDistortMaterial
        color="#7C3AED"
        roughness={0.1}
        metalness={0.9}
        distort={0.35}
        speed={2}
        envMapIntensity={3}
      />
    </mesh>
  );
}

// ── Main exported component ──────────────────────────────────────
export default function LogoJourney() {
  const groupRef = useRef();
  const scroll = useScroll();

  useFrame((state, delta) => {
    if (!groupRef.current) return;

    const t = scroll.offset; // 0 → 1

    /* ─── Position & scale targets per scroll phase ─── */
    let targetX = 0;
    let targetY = 0;
    let targetScale = 1.2;
    let rotX = delta * 0.3;
    let rotY = delta * 0.6;

    if (t < 0.25) {
      // HERO: centered, big, floating
      targetX = 0;
      targetY = 0;
      targetScale = 1.2;
      rotY = delta * 0.5;
    } else if (t < 0.60) {
      // FALLING: tumble to lower-left
      const p = (t - 0.25) / 0.35;
      const ease = 1 - Math.pow(1 - p, 3); // cubic ease-out
      targetX = THREE.MathUtils.lerp(0, -2.6, ease);
      targetY = THREE.MathUtils.lerp(0, -1.6, ease);
      targetScale = THREE.MathUtils.lerp(1.2, 0.65, ease);
      rotX = delta * (2 + p * 4);
      rotY = delta * (2 + p * 4);
    } else if (t < 0.80) {
      // WORKSPACE CORNER: settled, slow spin
      targetX = -2.6;
      targetY = -1.6;
      targetScale = 0.65;
      rotX = delta * 0.4;
      rotY = delta * 0.8;
    } else {
      // EXIT: shrink away
      const p = (t - 0.80) / 0.20;
      targetX = -2.6;
      targetY = -1.6;
      targetScale = THREE.MathUtils.lerp(0.65, 0, p);
    }

    /* ─── Smooth interpolation ─── */
    const lerpSpeed = 4;
    groupRef.current.position.x = THREE.MathUtils.lerp(groupRef.current.position.x, targetX, lerpSpeed * delta);
    groupRef.current.position.y = THREE.MathUtils.lerp(groupRef.current.position.y, targetY, lerpSpeed * delta);

    const currentScale = groupRef.current.scale.x;
    const newScale = THREE.MathUtils.lerp(currentScale, targetScale, lerpSpeed * delta);
    groupRef.current.scale.setScalar(newScale);

    /* ─── Continuous rotation ─── */
    groupRef.current.rotation.x += rotX;
    groupRef.current.rotation.y += rotY;
  });

  return (
    <group ref={groupRef}>
      <Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.5}>
        {/* Core nucleus */}
        <Nucleus />

        {/* Orbital rings */}
        <Ring radius={0.9} tube={0.04} color="#7C3AED" speed={0.6} phase={0} />
        <Ring radius={1.15} tube={0.025} color="#6366F1" speed={0.4} phase={1.2} />
        <Ring radius={1.38} tube={0.018} color="#EC4899" speed={0.25} phase={2.4} />

        {/* Point light that follows the shape */}
        <pointLight color="#7C3AED" intensity={3} distance={4} />
        <pointLight color="#EC4899" intensity={1.5} distance={3} position={[1, 1, 0]} />
      </Float>
    </group>
  );
}
