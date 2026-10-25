/**
 * Viewer3D.jsx
 * ───────────────────────────────────────────────────────────────
 * Edge-to-edge full-screen interactive 3D preview modal.
 *
 * Features:
 *  - Studio 3-point lighting (key + fill + rim)
 *  - HDRI environment (city preset for reflections)
 *  - OrbitControls with auto-rotate, zoom, pan
 *  - Floating Glassmorphism control panel
 *  - Download actions: STL, GLB, OBJ (toast feedback)
 *  - Transform mode toggles: Translate | Rotate | Scale
 *  - Share link copy
 *  - GSAP entry animation (scale + fade)
 */

import React, { Suspense, useState, useRef, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import {
  OrbitControls,
  Environment,
  ContactShadows,
  Center,
  MeshDistortMaterial,
  Grid,
  Float,
} from '@react-three/drei';
import {
  X, Download, Share2, Wand2, RotateCw, Maximize2,
  Check, ChevronDown, Box, Circle, TriangleRight, Gem,
  ZoomIn, ZoomOut
} from 'lucide-react';
import { gsap } from 'gsap';

/* ── 3D scene shapes ──────────────────────────────────────── */
const SHAPES = {
  box:         { label: 'Geometric',  geo: <boxGeometry args={[1.3, 1.3, 1.3]} />,         color: '#7C3AED', distort: 0.12 },
  sphere:      { label: 'Organic',    geo: <sphereGeometry args={[0.95, 64, 64]} />,        color: '#6366F1', distort: 0.30 },
  torus:       { label: 'Flow',       geo: <torusGeometry args={[0.7, 0.3, 32, 100]} />,    color: '#EC4899', distort: 0.08 },
  icosahedron: { label: 'Crystal',    geo: <icosahedronGeometry args={[0.95, 1]} />,         color: '#00D4FF', distort: 0.18 },
  cone:        { label: 'Pyramidal',  geo: <coneGeometry args={[0.85, 1.6, 32]} />,          color: '#F59E0B', distort: 0.05 },
};

/* ── Animated model inside the viewer ────────────────────── */
function ViewerModel({ shape }) {
  const cfg = SHAPES[shape] || SHAPES.box;

  return (
    <Center>
      <Float speed={1.2} rotationIntensity={0.1} floatIntensity={0.3}>
        <mesh castShadow receiveShadow>
          {cfg.geo}
          <MeshDistortMaterial
            color={cfg.color}
            roughness={0.04}
            metalness={0.95}
            distort={cfg.distort}
            speed={1.5}
            envMapIntensity={4}
          />
        </mesh>
        {/* Glow aura */}
        <pointLight color={cfg.color} intensity={4} distance={5} />
      </Float>
    </Center>
  );
}

/* ── Toast notification ───────────────────────────────────── */
function Toast({ message, visible }) {
  return (
    <div
      className={`
        fixed bottom-8 left-1/2 -translate-x-1/2 z-[200]
        flex items-center gap-2 px-5 py-3 rounded-2xl
        glass-control border border-white/20
        text-sm text-white font-medium
        transition-all duration-300
        ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'}
      `}
    >
      <Check size={16} className="text-green-400" />
      {message}
    </div>
  );
}

/* ── Main Viewer3D ─────────────────────────────────────────── */
export default function Viewer3D({ isOpen, onClose, initialShape = 'sphere' }) {
  const [shape, setShape] = useState(initialShape);
  const [autoRotate, setAutoRotate] = useState(true);
  const [toast, setToast] = useState({ msg: '', show: false });
  const [downloadOpen, setDownloadOpen] = useState(false);

  const modalRef = useRef(null);
  const cfg = SHAPES[shape] || SHAPES.box;

  /* ── Sync shape on open ─────────────────────────────────── */
  useEffect(() => {
    if (isOpen) setShape(initialShape);
  }, [isOpen, initialShape]);

  /* ── GSAP entry animation ──────────────────────────────── */
  useEffect(() => {
    if (isOpen && modalRef.current) {
      gsap.fromTo(
        modalRef.current,
        { opacity: 0, scale: 0.9 },
        { opacity: 1, scale: 1, duration: 0.4, ease: 'back.out(1.5)' }
      );
    }
  }, [isOpen]);

  /* ── Toast helper ──────────────────────────────────────── */
  const showToast = (msg) => {
    setToast({ msg, show: true });
    setTimeout(() => setToast({ msg: '', show: false }), 2500);
  };

  const handleDownload = (format) => {
    setDownloadOpen(false);
    showToast(`جاري تحميل النموذج بصيغة ${format}...`);
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText('https://bu3d.ai/view/demo-xyz').catch(() => {});
    showToast('تم نسخ رابط المشاركة ✓');
  };

  const handleImprove = () => {
    showToast('جاري إرسال النموذج للتحسين بالذكاء الاصطناعي...');
  };

  /* ── Close ──────────────────────────────────── */
  const handleClose = () => {
    if (modalRef.current) {
      gsap.to(modalRef.current, {
        opacity: 0,
        scale: 0.9,
        duration: 0.3,
        ease: 'power2.in',
        onComplete: onClose,
      });
    } else {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* ── Backdrop ─────────────────────────────────────── */}
      <div
        className="fixed inset-0 z-[90] bg-black/70 backdrop-blur-sm transition-opacity duration-300"
        onClick={handleClose}
      />

      {/* ── Modal (edge-to-edge) ──────────────────────────── */}
      <div
        ref={modalRef}
        className="fixed inset-0 z-[100] flex flex-col"
        style={{ background: 'linear-gradient(135deg, #050506 0%, #0a0a14 100%)' }}
      >

        {/* ── Top bar ────────────────────────────────────── */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/8 bg-black/30 backdrop-blur-sm flex-shrink-0">
          <div className="flex items-center gap-3">
            {/* Shape pill */}
            <div
              className="w-8 h-8 rounded-xl flex items-center justify-center"
              style={{ background: `${cfg.color}20`, border: `1px solid ${cfg.color}40` }}
            >
              <div className="w-3 h-3 rounded-sm" style={{ background: cfg.color }} />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">معاينة النموذج الثلاثي الأبعاد</h2>
              <p className="text-xs text-muted-foreground">{cfg.label} · BU3D.ai</p>
            </div>
          </div>

          {/* Status + close */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 status-live inline-block" />
              PBR · ACES
            </div>
            <button
              onClick={handleClose}
              className="w-9 h-9 rounded-xl bg-white/5 hover:bg-white/15 border border-white/10 flex items-center justify-center text-muted-foreground hover:text-white transition-all cursor-pointer"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* ── 3D Canvas ─────────────────────────────────── */}
        <div className="flex-1 relative overflow-hidden">
          <Canvas
            shadows
            camera={{ position: [0, 0, 4.5], fov: 45 }}
            gl={{ antialias: true, alpha: false, toneMapping: 4 /* ACESFilmic */ }}
          >
            <color attach="background" args={['#050506']} />

            <Suspense fallback={null}>
              {/* ── Studio lighting ── */}
              {/* Key light */}
              <spotLight
                position={[8, 10, 8]}
                angle={0.2}
                penumbra={0.8}
                intensity={5}
                castShadow
                shadow-mapSize={[2048, 2048]}
                color="#ffffff"
              />
              {/* Fill light */}
              <directionalLight position={[-6, 4, -4]} intensity={1.5} color="#a78bfa" />
              {/* Rim/back light */}
              <pointLight position={[0, -3, -6]} intensity={2} color={cfg.color} />
              {/* Ambient */}
              <ambientLight intensity={0.4} />

              {/* Environment HDRI */}
              <Environment preset="city" />

              {/* The model */}
              <ViewerModel shape={shape} />

              {/* Floor shadow */}
              <ContactShadows
                position={[0, -2, 0]}
                opacity={0.6}
                scale={12}
                blur={2.5}
                far={6}
                color={cfg.color}
              />

              {/* Subtle grid */}
              <Grid
                infiniteGrid
                position={[0, -2.02, 0]}
                fadeDistance={30}
                cellSize={0.5}
                sectionSize={3}
                cellColor="rgba(255,255,255,0.02)"
                sectionColor="rgba(255,255,255,0.05)"
              />

              {/* Orbit controls */}
              <OrbitControls
                makeDefault
                autoRotate={autoRotate}
                autoRotateSpeed={1.5}
                enableDamping
                dampingFactor={0.05}
                minPolarAngle={0}
                maxPolarAngle={Math.PI * 0.85}
                minDistance={2}
                maxDistance={10}
              />
            </Suspense>
          </Canvas>

          {/* ── Shape switcher (top-right of canvas) ─── */}
          <div className="absolute top-4 right-4 flex flex-col gap-2">
            {Object.entries(SHAPES).map(([key, val]) => (
              <button
                key={key}
                onClick={() => setShape(key)}
                title={val.label}
                className={`
                  w-9 h-9 rounded-xl border flex items-center justify-center
                  text-xs font-bold transition-all duration-200 cursor-pointer
                  ${shape === key
                    ? 'border-transparent text-white'
                    : 'border-white/10 bg-black/40 text-muted-foreground hover:text-white hover:bg-white/10'}
                `}
                style={shape === key ? { background: `${val.color}30`, borderColor: `${val.color}60` } : {}}
              >
                {key === 'box' && <Box size={14} />}
                {key === 'sphere' && <Circle size={14} />}
                {key === 'torus' && <RotateCw size={14} />}
                {key === 'icosahedron' && <Gem size={14} />}
                {key === 'cone' && <TriangleRight size={14} />}
              </button>
            ))}
          </div>

          {/* ── Auto-rotate toggle (top-left) ────────── */}
          <button
            onClick={() => setAutoRotate((v) => !v)}
            className={`
              absolute top-4 left-4 flex items-center gap-2 px-3 py-2
              rounded-xl border text-xs font-medium transition-all cursor-pointer
              ${autoRotate
                ? 'bg-primary/20 border-primary/40 text-primary'
                : 'bg-black/40 border-white/10 text-muted-foreground hover:text-white'}
            `}
          >
            <RotateCw size={13} className={autoRotate ? 'animate-spin' : ''} style={{ animationDuration: '3s' }} />
            <span className="hidden sm:inline">{autoRotate ? 'إيقاف الدوران' : 'تشغيل الدوران'}</span>
          </button>
        </div>

        {/* ── Floating Glass Control Panel ─────────────────── */}
        <div className="flex-shrink-0 px-4 py-4">
          <div className="max-w-2xl mx-auto glass-control rounded-2xl p-4">
            <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3">

              {/* Download dropdown */}
              <div className="relative">
                <button
                  onClick={() => setDownloadOpen((v) => !v)}
                  className="flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-xl font-medium text-sm transition-all shadow-[0_0_20px_-5px_rgba(124,58,237,0.5)] cursor-pointer"
                >
                  <Download size={15} />
                  تحميل
                  <ChevronDown size={13} className={`transition-transform ${downloadOpen ? 'rotate-180' : ''}`} />
                </button>

                {downloadOpen && (
                  <div className="absolute bottom-full mb-2 right-0 glass-control rounded-xl overflow-hidden border border-white/10 min-w-[130px] z-10">
                    {['STL', 'GLB', 'OBJ', 'FBX'].map((fmt) => (
                      <button
                        key={fmt}
                        onClick={() => handleDownload(fmt)}
                        className="block w-full text-right px-4 py-2.5 text-sm text-white/80 hover:text-white hover:bg-white/8 transition-colors cursor-pointer"
                      >
                        .{fmt}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Improve */}
              <button
                onClick={handleImprove}
                className="flex items-center gap-2 px-5 py-2.5 bg-white/8 hover:bg-white/15 border border-white/10 text-white rounded-xl font-medium text-sm transition-all cursor-pointer"
              >
                <Wand2 size={15} />
                <span className="hidden sm:inline">تحسين</span>
              </button>

              {/* Share */}
              <button
                onClick={handleCopyLink}
                className="flex items-center gap-2 px-5 py-2.5 bg-white/8 hover:bg-white/15 border border-white/10 text-white rounded-xl font-medium text-sm transition-all cursor-pointer"
              >
                <Share2 size={15} />
                <span className="hidden sm:inline">مشاركة</span>
              </button>

              {/* Zoom hint */}
              <div className="hidden md:flex items-center gap-1.5 px-3 py-2.5 rounded-xl bg-white/4 border border-white/8 text-muted-foreground text-xs">
                <ZoomIn size={13} />
                <span>اسحب للتدوير</span>
                <span className="mx-1.5 opacity-40">·</span>
                <ZoomOut size={13} />
                <span>عجلة للتكبير</span>
              </div>

            </div>
          </div>
        </div>
      </div>

      {/* ── Toast ─────────────────────────────────────────── */}
      <Toast message={toast.msg} visible={toast.show} />
    </>
  );
}
