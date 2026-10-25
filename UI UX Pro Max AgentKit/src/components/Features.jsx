/**
 * Features.jsx
 * ───────────────────────────────────────────────────────────────
 * "How It Works" section using a Bento Grid layout.
 * 6 cards in an asymmetric grid with glassmorphism and
 * GSAP-powered scroll-reveal (stagger on viewport entry).
 */

import React, { useEffect, useRef, useState } from 'react';
import {
  MessageSquare, Cpu, Eye, Download, Layers, Zap
} from 'lucide-react';

const FEATURES = [
  {
    icon: MessageSquare,
    title: 'أدخل وصفك',
    desc: 'اكتب وصفاً نصياً أو ارفع صورة مرجعية. المنصة تفهم العربية والإنجليزية.',
    color: '#7C3AED',
    span: 'col-span-1',
    size: 'large',
  },
  {
    icon: Cpu,
    title: 'الذكاء الاصطناعي يعمل',
    desc: 'نماذج AI متقدمة تحلل مدخلاتك وتولّد الهيكل الثلاثي الأبعاد خلال ثوانٍ.',
    color: '#6366F1',
    span: 'col-span-1',
    size: 'normal',
  },
  {
    icon: Layers,
    title: '٤ خيارات إبداعية',
    desc: 'احصل على أربعة تصاميم مختلفة لكل فكرة واختر الأنسب.',
    color: '#EC4899',
    span: 'col-span-1',
    size: 'normal',
  },
  {
    icon: Eye,
    title: 'معاينة تفاعلية',
    desc: 'افتح عارض ثلاثي الأبعاد كامل الشاشة مع إمكانية التدوير والتكبير والتحريك.',
    color: '#00D4FF',
    span: 'col-span-1 md:col-span-2',
    size: 'wide',
  },
  {
    icon: Zap,
    title: 'تحسين فوري',
    desc: 'أرسل النموذج للتحسين بنقرة واحدة — الذكاء الاصطناعي يُصقل التفاصيل.',
    color: '#F59E0B',
    span: 'col-span-1',
    size: 'normal',
  },
  {
    icon: Download,
    title: 'تحميل احترافي',
    desc: 'صادر بصيغ STL، GLB، OBJ جاهزة للطباعة ثلاثية الأبعاد أو استخدامها في أي محرك.',
    color: '#10B981',
    span: 'col-span-1',
    size: 'normal',
  },
];

export default function Features() {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.2 } // Trigger at 20%
    );

    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section id="features" ref={sectionRef} className="py-24 relative max-w-5xl mx-auto px-4 sm:px-6">

      {/* Ambient blob */}
      <div
        className="blob w-80 h-80 -top-20 -right-20 opacity-20"
        style={{ background: 'radial-gradient(circle, #7C3AED, transparent 70%)' }}
      />

      {/* Heading */}
      <div className="text-center mb-14 relative z-10">
        <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-neon/10 border border-neon/20 text-neon text-sm font-medium mb-4">
          <Zap size={14} />
          كيف يعمل BU3D.ai
        </span>
        <h2 className="text-3xl md:text-4xl font-bold mb-3">
          من الفكرة إلى الواقع الثلاثي
        </h2>
        <p className="text-muted-foreground text-lg max-w-xl mx-auto">
          ستة خطوات تحوّل كلماتك إلى نماذج ثلاثية الأبعاد جاهزة للاستخدام.
        </p>
      </div>

      {/* Bento grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 relative z-10">
        {FEATURES.map((feat, i) => {
          const Icon = feat.icon;
          return (
            <div
              key={i}
              className={`
                feature-card group relative rounded-2xl p-6 overflow-hidden
                theme-card
                hover:border-white/20 transition-all duration-300
                cursor-default
                ${feat.span}
                ${feat.size === 'large' ? 'md:row-span-2 md:p-8' : ''}
              `}
              style={{
                opacity: isVisible ? 1 : 0,
                transform: isVisible ? 'translateY(0)' : 'translateY(20px)',
                transition: `all 0.6s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.08}s`
              }}
            >
              {/* Icon */}
              <div
                className="w-12 h-12 rounded-2xl flex items-center justify-center mb-5 transition-transform duration-300 group-hover:scale-110"
                style={{ background: `${feat.color}15`, border: `1px solid ${feat.color}30` }}
              >
                <Icon size={22} style={{ color: feat.color }} />
              </div>

              {/* Step number */}
              <div className="absolute top-4 right-4 text-[11px] font-mono text-white/20">
                {String(i + 1).padStart(2, '0')}
              </div>

              <h3 className="text-lg font-bold mb-2 text-white">{feat.title}</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">{feat.desc}</p>

              {/* Hover glow */}
              <div
                className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none rounded-2xl"
                style={{ background: `radial-gradient(circle at 30% 30%, ${feat.color}0D 0%, transparent 60%)` }}
              />

              {/* Bottom accent line */}
              <div
                className="absolute bottom-0 left-0 h-0.5 w-0 group-hover:w-full transition-all duration-500 rounded-full"
                style={{ background: `linear-gradient(90deg, ${feat.color}, transparent)` }}
              />
            </div>
          );
        })}
      </div>
    </section>
  );
}
