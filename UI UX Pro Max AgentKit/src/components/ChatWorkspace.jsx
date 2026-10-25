/**
 * ChatWorkspace.jsx
 * ───────────────────────────────────────────────────────────────
 * The core conversational AI generation interface.
 *
 * Flow:
 *  1. idle    — welcome screen with suggestion chips
 *  2. generating — animated loading with cycling status messages
 *  3. done    — 4 result cards with inline 3D previews
 *
 * On card click → parent opens Viewer3D modal
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Send, Sparkles, Loader2, Image as ImageIcon,
  Paperclip, Mic, RotateCcw, Wand2
} from 'lucide-react';
import { gsap } from 'gsap';
import ModelCard3D from './ModelCard3D';

/* ── Generation result options ─────────────────────────────── */
const MODELS = [
  {
    id: 1,
    name: 'خيار ١: تصميم عضوي',
    shape: 'sphere',
    glow: 'glow-primary',
    tag: 'Organic'
  },
  {
    id: 2,
    name: 'خيار ٢: هندسة صلبة',
    shape: 'box',
    glow: '',
    tag: 'Geometric'
  },
  {
    id: 3,
    name: 'خيار ٣: تصميم متدفق',
    shape: 'torus',
    glow: 'glow-accent',
    tag: 'Flow'
  },
  {
    id: 4,
    name: 'خيار ٤: بلوري حاد',
    shape: 'icosahedron',
    glow: 'glow-neon',
    tag: 'Crystal'
  },
];

/* ── Loading status messages ───────────────────────────────── */
const LOADING_MSGS = [
  { icon: '🔍', text: 'جاري تحليل المدخلات وفهم الأبعاد...' },
  { icon: '🏗️', text: 'بناء الهيكل الهندسي الأساسي...' },
  { icon: '✨', text: 'تطبيق الخامات والإضاءة التشعبية...' },
  { icon: '🎨', text: 'رسم الجزيئات والتفاصيل الدقيقة...' },
  { icon: '🚀', text: 'اللمسات الأخيرة... النماذج جاهزة!' },
];

/* ── Prompt suggestions ────────────────────────────────────── */
const SUGGESTIONS = [
  'كرسي مكتبي عصري بذراعين',
  'إناء نباتات هندسي بزوايا حادة',
  'مصباح طاولة بشكل مثلث مجوف',
  'هيكل معماري طوري مستقبلي',
];

export default function ChatWorkspace({ onSelectModel }) {
  const [prompt, setPrompt] = useState('');
  const [status, setStatus] = useState('idle'); // idle | generating | done
  const [loadingStep, setLoadingStep] = useState(0);
  const [progress, setProgress] = useState(0);

  const cardsRef = useRef(null);
  const inputRef = useRef(null);

  /* ── Loading animation ─────────────────────────────────── */
  useEffect(() => {
    let stepInterval;
    let progressInterval;

    if (status === 'generating') {
      setProgress(0);
      setLoadingStep(0);

      // Cycle through messages
      stepInterval = setInterval(() => {
        setLoadingStep((prev) => (prev + 1) % LOADING_MSGS.length);
      }, 1800);

      // Animate progress bar
      progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 95) return 95;
          return prev + Math.random() * 8;
        });
      }, 400);
    } else {
      setLoadingStep(0);
      setProgress(0);
    }

    return () => {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
    };
  }, [status]);

  /* ── Animate cards in with GSAP when done ──────────────── */
  useEffect(() => {
    if (status === 'done' && cardsRef.current) {
      const cards = cardsRef.current.querySelectorAll('.model-card');
      gsap.fromTo(
        cards,
        { opacity: 0, y: 40, scale: 0.9 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.6,
          stagger: 0.12,
          ease: 'back.out(1.4)',
        }
      );
    }
  }, [status]);

  /* ── Submit handler ────────────────────────────────────── */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim() || status === 'generating') return;

    setStatus('generating');

    // Simulate 6-second AI generation
    setTimeout(() => {
      setProgress(100);
      setTimeout(() => setStatus('done'), 300);
    }, 6000);
  };

  /* ── Suggestion chip click ─────────────────────────────── */
  const handleSuggestion = (text) => {
    setPrompt(text);
    inputRef.current?.focus();
  };

  /* ── Reset ─────────────────────────────────────────────── */
  const handleReset = () => {
    setStatus('idle');
    setPrompt('');
  };

  return (
    <section id="workspace" className="py-16 relative max-w-5xl mx-auto px-4 sm:px-6">

      {/* Section label */}
      <div className="text-center mb-10">
        <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-4">
          <Wand2 size={14} />
          مساحة التوليد
        </span>
        <h2 className="text-3xl md:text-4xl font-bold mb-3">
          أخبرنا بما تتخيله
        </h2>
        <p className="text-muted-foreground text-lg max-w-lg mx-auto">
          اكتب وصفاً بالعربية أو الإنجليزية، وسيقوم BU3D.ai بتوليد ٤ نماذج ثلاثية الأبعاد فورياً.
        </p>
      </div>

      {/* Main workspace card */}
      <div className="glass-panel rounded-3xl overflow-hidden">

        {/* ── IDLE STATE ── */}
        {status === 'idle' && (
          <div className="p-8 min-h-[320px] flex flex-col items-center justify-center">
            {/* Animated icon */}
            <div className="relative mb-8">
              <div className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 flex items-center justify-center rounded-xl bg-primary text-white shadow-lg shadow-primary/30 hover:scale-105 transition-transform cursor-pointer" />
              <div className="absolute inset-0 rounded-full bg-primary/5 animate-ping" />
            </div>

            <p className="text-muted-foreground text-center mb-8 text-lg">
              في انتظار إبداعك...
            </p>

            {/* Suggestion chips */}
            <div className="flex flex-wrap gap-2 justify-center max-w-lg">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggestion(s)}
                  className="px-4 py-2 rounded-full border border-black/10 dark:border-white/10 bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 hover:border-primary/40 text-sm text-foreground/70 hover:text-foreground transition-all duration-200 cursor-pointer"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* ── GENERATING STATE ── */}
        {status === 'generating' && (
          <div className="p-10 min-h-[320px] flex flex-col items-center justify-center gap-6">
            {/* Spinning rings */}
            <div className="relative w-24 h-24">
              <div className="absolute inset-0 rounded-full border-2 border-primary/20 animate-spin" style={{ animationDuration: '3s' }} />
              <div className="absolute inset-2 rounded-full border-2 border-t-primary border-transparent animate-spin" style={{ animationDuration: '1.5s' }} />
              <div className="absolute inset-4 rounded-full border-2 border-b-accent border-transparent animate-spin" style={{ animationDuration: '1s', animationDirection: 'reverse' }} />
              <div className="absolute inset-0 flex items-center justify-center">
                <Sparkles className="text-primary w-6 h-6 sparkle-pulse" />
              </div>
            </div>

            {/* Cycling message */}
            <div className="h-10 overflow-hidden flex items-center">
              <p
                key={loadingStep}
                className="text-lg font-medium text-center animate-in fade-in slide-in-from-bottom-3 duration-500"
              >
                <span className="me-2">{LOADING_MSGS[loadingStep].icon}</span>
                {LOADING_MSGS[loadingStep].text}
              </p>
            </div>

            {/* Progress bar */}
            <div className="w-full max-w-sm">
              <div className="h-1.5 rounded-full bg-black/5 dark:bg-white/5 overflow-hidden progress-shimmer">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-primary via-secondary to-accent transition-all duration-300 relative z-10"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground text-center mt-2 animate-pulse">
                يرجى الانتظار، السحر يحدث الآن ✨
              </p>
            </div>
          </div>
        )}

        {/* ── RESULTS STATE ── */}
        {status === 'done' && (
          <div ref={cardsRef} className="p-6 sm:p-8">
            {/* Results header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold text-white">اختر النموذج المناسب</h3>
                <p className="text-sm text-muted-foreground mt-1">انقر على أي نموذج لمعاينته بشكل كامل في الفضاء الثلاثي</p>
              </div>
              <button
                onClick={handleReset}
                className="flex items-center gap-2 px-3 py-2 rounded-xl bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 border border-black/5 dark:border-white/10 text-muted-foreground hover:text-foreground transition-all text-sm cursor-pointer"
              >
                <RotateCcw size={14} />
                <span className="hidden sm:inline">إعادة</span>
              </button>
            </div>

            {/* 4 model cards in 2×2 grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {MODELS.map((model) => (
                <div key={model.id} className="model-card">
                  <ModelCard3D
                    shape={model.shape}
                    label={model.name}
                    glow={model.glow}
                    onClick={() => onSelectModel(model.shape)}
                  />
                </div>
              ))}
            </div>

            {/* Tag row */}
            <div className="flex flex-wrap gap-2 mt-5 justify-center">
              {MODELS.map((m) => (
                <span key={m.id} className="text-[11px] px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-muted-foreground">
                  {m.tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* ── INPUT BAR (always visible at bottom) ── */}
        <div className="p-4 sm:p-6 border-t border-white/5 bg-black/20">
          <form onSubmit={handleSubmit} className="flex items-end gap-3">
            {/* Image upload button */}
            <button
              type="button"
              title="رفع صورة"
              className="flex-shrink-0 w-11 h-11 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center text-muted-foreground hover:text-white transition-all cursor-pointer"
            >
              <Paperclip size={18} />
            </button>

            {/* Text input */}
            <div className="flex-1 relative">
              <div className="relative theme-card rounded-2xl p-1 mb-4">
              <textarea
                ref={inputRef}
                value={prompt}
                onChange={(e) => {
                  setPrompt(e.target.value);
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                placeholder="صف ما تريد تصميمه... مثال: كرسي فراهي بتصميم مستقبلي"
                disabled={status === 'generating'}
                rows={1}
                className="
                  w-full bg-black/40 border border-white/15 rounded-2xl
                  py-3.5 px-5 text-white placeholder-white/30
                  focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50
                  disabled:opacity-50 resize-none leading-relaxed
                  transition-all duration-200 text-sm
                "
              />
              </div>
            </div>

            {/* Voice button */}
            <button
              type="button"
              title="إدخال صوتي"
              className="flex-shrink-0 w-11 h-11 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center text-muted-foreground hover:text-white transition-all cursor-pointer"
            >
              <Mic size={18} />
            </button>

            {/* Submit button */}
            <button
              type="submit"
              disabled={!prompt.trim() || status === 'generating'}
              id="generate-btn"
              className="
                flex-shrink-0 w-11 h-11 rounded-2xl
                bg-primary hover:bg-primary/90
                disabled:bg-white/10 disabled:text-white/30
                text-white flex items-center justify-center
                transition-all duration-200 shadow-[0_0_20px_-5px_rgba(124,58,237,0.6)]
                disabled:shadow-none cursor-pointer
              "
            >
              {status === 'generating'
                ? <Loader2 className="w-5 h-5 animate-spin" />
                : <Send className="w-5 h-5" />
              }
            </button>
          </form>

          <p className="text-xs text-muted-foreground text-center mt-3">
            النماذج مولّدة بالذكاء الاصطناعي · اضغط Enter للإرسال أو Shift+Enter لسطر جديد
          </p>
        </div>
      </div>
    </section>
  );
}
