/**
 * App.jsx — BU3D.ai Main Application
 * ─────────────────────────────────────────────────────────────
 * Architecture (fixed canvas + standard scroll):
 *
 *  ┌─ Fixed WebGL Canvas (z-1, pointer-events-none)
 *  │   └─ ScrollControls (drives 3D logo animation)
 *  │       └─ LogoJourney (3D object that falls with scroll)
 *  │
 *  └─ Normal HTML page (z-10, standard browser scroll)
 *      ├─ Navbar (fixed)
 *      ├─ Hero section
 *      ├─ Features
 *      ├─ ChatWorkspace
 *      ├─ Pricing
 *      └─ Footer
 *
 *  ├─ Sidebar (z-70)
 *  └─ Viewer3D (z-100)
 */

import React, { useState, useEffect, useRef, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { ScrollControls, Environment } from '@react-three/drei';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import LogoJourney from './components/LogoJourney';
import Viewer3D from './components/Viewer3D';
import ChatWorkspace from './components/ChatWorkspace';
import Features from './components/Features';
import Pricing from './components/Pricing';
import Footer from './components/Footer';
import Sidebar from './components/Sidebar';
import {
  History, UploadCloud, ChevronDown,
  Sparkles, ArrowRight, Play, Menu, X as XIcon, Sun, Moon
} from 'lucide-react';
import { ThemeProvider, useTheme } from './ThemeContext';

gsap.registerPlugin(ScrollTrigger);

/* ──────────────────────────────────────────────
   NAVBAR
   ────────────────────────────────────────────── */
function Navbar({ onHistoryOpen }) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isDark, toggleTheme } = useTheme();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const navLinks = [
    { href: '#features', label: 'كيف يعمل' },
    { href: '#workspace', label: 'مساحة العمل' },
    { href: '#pricing', label: 'الأسعار' },
  ];

  return (
    <nav
      className={`
        fixed top-0 left-0 right-0 z-40 transition-all duration-500
        ${scrolled
          ? 'bg-black/75 dark:bg-black/75 light:bg-white/75 backdrop-blur-xl border-b border-white/8 dark:border-white/8 light:border-black/5 py-3'
          : 'bg-transparent py-5'}
      `}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 flex items-center justify-between">

        {/* Logo */}
        <a href="#" className="flex items-center gap-2.5 group">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-sm shadow-lg transition-transform group-hover:scale-110"
            style={{ background: 'linear-gradient(135deg, #7C3AED, #6366F1, #EC4899)' }}
          >
            BU
          </div>
          <div className="leading-none">
            <span className="font-black text-xl text-white tracking-tight">BU3D</span>
            <span className="text-primary font-light">.ai</span>
          </div>
        </a>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="hover:text-white transition-colors relative group"
            >
              {link.label}
              <span className="absolute -bottom-0.5 left-0 w-0 h-0.5 bg-primary group-hover:w-full transition-all duration-300 rounded-full" />
            </a>
          ))}
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="w-9 h-9 rounded-xl bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 border border-black/5 dark:border-white/8 flex items-center justify-center text-muted-foreground hover:text-foreground transition-all cursor-pointer"
            title="تبديل المظهر"
          >
            {isDark ? (
              <Moon size={18} className="theme-icon-dark text-white" />
            ) : (
              <Sun size={18} className="theme-icon-light text-[#1A1A2E]" />
            )}
          </button>

          <button
            onClick={onHistoryOpen}
            className="hidden sm:flex w-9 h-9 rounded-xl bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 border border-black/5 dark:border-white/8 items-center justify-center text-muted-foreground hover:text-foreground transition-all cursor-pointer"
            title="سجل النماذج"
          >
            <History size={18} />
          </button>

          <a
            href="#workspace"
            className="hidden sm:flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition-all hover:opacity-90 shadow-[0_0_20px_-5px_rgba(124,58,237,0.4)]"
            style={{ background: 'linear-gradient(135deg, #7C3AED, #6366F1)' }}
          >
            ابدأ مجاناً
            <ArrowRight size={15} className="rtl:rotate-180" />
          </a>

          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden w-9 h-9 rounded-xl bg-white/5 border border-white/8 flex items-center justify-center text-muted-foreground hover:text-white transition-all cursor-pointer"
          >
            {mobileOpen ? <XIcon size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-white/8 bg-black/85 backdrop-blur-xl px-4 py-4 space-y-1">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setMobileOpen(false)}
              className="block px-4 py-3 rounded-xl text-sm text-white/70 hover:text-white hover:bg-white/5 transition-all"
            >
              {link.label}
            </a>
          ))}
          <a
            href="#workspace"
            onClick={() => setMobileOpen(false)}
            className="block px-4 py-3 rounded-xl text-sm text-white font-bold text-center mt-2"
            style={{ background: 'linear-gradient(135deg, #7C3AED, #6366F1)' }}
          >
            ابدأ مجاناً
          </a>
        </div>
      )}
    </nav>
  );
}

/* ──────────────────────────────────────────────
   HERO SECTION
   ────────────────────────────────────────────── */
function HeroSection({ onDemoClick }) {
  const ref = useRef(null);
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    if (!ref.current) return;
    const tl = gsap.timeline({ delay: 0.4 });
    tl.fromTo('.hero-badge',  { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' })
      .fromTo('.hero-h1',    { opacity: 0, y: 35 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' }, '-=0.3')
      .fromTo('.hero-p',     { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }, '-=0.4')
      .fromTo('.hero-ctas',  { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }, '-=0.3')
      .fromTo('.hero-scroll',{ opacity: 0 },         { opacity: 1,       duration: 0.5,                    }, '-=0.2');
  }, []);

  return (
    <section
      ref={ref}
      className="relative h-screen flex flex-col items-center justify-center px-4 sm:px-6 pt-20 overflow-hidden"
    >
      {/* Dot grid */}
      <div className="absolute inset-0 dot-grid opacity-25 pointer-events-none" />

      {/* Ambient blobs with Parallax (scrolls at 0.5x) and CSS animations */}
      <div 
        className="blob parallax-blob absolute w-[500px] h-[500px] top-[-10%] right-[-5%] opacity-25 pointer-events-none ring-rotate-cw ring-glow-breathe"
        style={{ 
          background: 'radial-gradient(circle, #7C3AED 0%, transparent 65%)',
          transform: `translateY(${scrollY * 0.5}px)` 
        }} 
      />
      <div 
        className="blob parallax-blob absolute w-[400px] h-[400px] bottom-[-5%] left-[-5%] opacity-15 pointer-events-none ring-rotate-ccw ring-glow-breathe"
        style={{ 
          background: 'radial-gradient(circle, #6366F1 0%, transparent 65%)', 
          animationDelay: '4s',
          transform: `translateY(${scrollY * 0.5}px)` 
        }} 
      />

      <div className="max-w-4xl w-full text-center relative z-10">
        {/* Badge */}
        <div className="hero-badge opacity-0 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/25 text-primary text-sm font-medium mb-8">
          <Sparkles size={14} />
          الجيل الجديد من توليد النماذج ثلاثية الأبعاد
        </div>

        {/* Headline */}
        <h1 className="hero-h1 opacity-0 text-5xl sm:text-6xl md:text-7xl font-black tracking-tight mb-6 leading-tight">
          <span className="text-white">حوّل كلماتك</span><br />
          <span
            className="text-transparent bg-clip-text"
            style={{ backgroundImage: 'linear-gradient(135deg, #7C3AED 0%, #6366F1 40%, #EC4899 70%, #00D4FF 100%)' }}
          >
            إلى عوالم ثلاثية
          </span>
        </h1>

        {/* Sub-headline */}
        <p className="hero-p opacity-0 text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
          BU3D.ai يحوّل أفكارك النصية والصور إلى نماذج ثلاثية الأبعاد احترافية في ثوانٍ.
          جاهزة للطباعة والاستخدام الفوري.
        </p>

        {/* CTAs */}
        <div className="hero-ctas opacity-0 flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href="#workspace"
            className="flex items-center gap-2.5 px-8 py-4 rounded-2xl text-white font-bold text-base transition-all hover:scale-105 shadow-[0_0_40px_-5px_rgba(124,58,237,0.5)] hover:shadow-[0_0_60px_-5px_rgba(124,58,237,0.7)]"
            style={{ background: 'linear-gradient(135deg, #7C3AED, #6366F1)' }}
          >
            <Sparkles size={18} />
            ابدأ التوليد مجاناً
          </a>
          <button
            onClick={onDemoClick}
            className="flex items-center gap-2.5 px-8 py-4 rounded-2xl text-white font-bold text-base glass border border-white/15 hover:border-white/30 hover:bg-white/8 transition-all cursor-pointer"
          >
            <Play size={16} className="text-primary" />
            شاهد العرض التجريبي
          </button>
        </div>

        {/* Scroll hint */}
        <div className="hero-scroll opacity-0 mt-16 flex flex-col items-center gap-2 text-muted-foreground">
          <p className="text-xs tracking-widest uppercase">اسحب لبدء الرحلة</p>
          <ChevronDown size={20} className="scroll-bounce" />
        </div>
      </div>
    </section>
  );
}

/* ──────────────────────────────────────────────
   MAIN APP CONTENT
   ────────────────────────────────────────────── */
function AppContent() {
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [selectedShape, setSelectedShape] = useState('sphere');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const handleSelectModel = (shape) => {
    setSelectedShape(shape);
    setIsViewerOpen(true);
  };

  /* Drag overlay */
  useEffect(() => {
    let timer;
    const onDragOver = (e) => { e.preventDefault(); setIsDragging(true); clearTimeout(timer); };
    const onDragLeave = () => { timer = setTimeout(() => setIsDragging(false), 200); };
    const onDrop = (e) => { e.preventDefault(); setIsDragging(false); };
    window.addEventListener('dragover', onDragOver);
    window.addEventListener('dragleave', onDragLeave);
    window.addEventListener('drop', onDrop);
    return () => {
      window.removeEventListener('dragover', onDragOver);
      window.removeEventListener('dragleave', onDragLeave);
      window.removeEventListener('drop', onDrop);
    };
  }, []);

  return (
    <div className="relative bg-background text-foreground font-sans overflow-x-hidden theme-transition">

      {/* ─── Fixed WebGL Canvas — 3D Logo only ─── */}
      <Canvas
        camera={{ position: [0, 0, 5], fov: 45 }}
        className="fixed inset-0 z-[1] pointer-events-none"
        gl={{ antialias: true, alpha: true }}
        style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh' }}
      >
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 5]} intensity={1.2} />
        <Environment preset="city" />

        {/* ScrollControls tied to window scroll so offset tracks the page */}
        <ScrollControls pages={7} damping={0.3}>
          <Suspense fallback={null}>
            <LogoJourney />
          </Suspense>
        </ScrollControls>
      </Canvas>

      {/* ─── Fixed Navbar ─── */}
      <Navbar onHistoryOpen={() => setIsSidebarOpen(true)} />

      {/* ─── Normal HTML page (z-10 above canvas) ─── */}
      <div className="relative z-10">

        {/* Hero */}
        <HeroSection onDemoClick={() => handleSelectModel('torus')} />

        {/* Features */}
        <Features />

        {/* Workspace */}
        <ChatWorkspace onSelectModel={handleSelectModel} />

        {/* Pricing */}
        <Pricing />

        {/* Footer */}
        <Footer />
      </div>

      {/* ─── Sidebar ─── */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onSelectHistory={handleSelectModel}
      />

      {/* ─── 3D Viewer Modal ─── */}
      <Viewer3D
        isOpen={isViewerOpen}
        onClose={() => setIsViewerOpen(false)}
        initialShape={selectedShape}
      />

      {/* ─── Drag overlay ─── */}
      {isDragging && (
        <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/70 backdrop-blur-lg border-2 border-dashed border-primary/60 animate-in fade-in duration-200">
          <div className="flex flex-col items-center text-center p-10 glass-panel rounded-3xl">
            <div className="w-20 h-20 rounded-full bg-primary/15 flex items-center justify-center mb-5 border border-primary/30">
              <UploadCloud size={40} className="text-primary animate-bounce" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">أفلت الصورة هنا</h2>
            <p className="text-muted-foreground">سنحوّلها إلى نموذج ثلاثي الأبعاد فوراً</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
