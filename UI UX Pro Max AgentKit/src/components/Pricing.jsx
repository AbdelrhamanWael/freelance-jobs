/**
 * Pricing.jsx
 * ───────────────────────────────────────────────────────────────
 * 3-column subscription tiers with:
 *  - Glassmorphism cards
 *  - JS mousemove-driven 3D perspective tilt (per card)
 *  - GSAP scroll-trigger reveal
 *  - Detailed feature lists per plan
 *  - Highlighted "Most Popular" centre card
 */

import React, { useRef, useEffect } from 'react';
import { Check, X, Star, Zap, Shield, Crown } from 'lucide-react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

/* ── Pricing data ─────────────────────────────────────────── */
const PLANS = [
  {
    id: 'starter',
    icon: Zap,
    name: 'Starter',
    nameAr: 'المبتدئ',
    price: '$19',
    period: '/شهر',
    conversions: '50 نموذج/شهر',
    tagline: 'مثالي للأفراد والهواة',
    color: '#10B981',
    glow: 'rgba(16, 185, 129, 0.25)',
    features: [
      { text: '50 تحويل نصي-3D شهرياً', included: true },
      { text: 'رفع الصور للتوليد', included: true },
      { text: 'معاينة ثلاثية الأبعاد', included: true },
      { text: 'تحميل بصيغة STL', included: true },
      { text: 'تحميل GLB & OBJ', included: false },
      { text: 'تحسين النموذج بالذكاء الاصطناعي', included: false },
      { text: 'دعم فني أولوية', included: false },
    ],
  },
  {
    id: 'creator',
    icon: Star,
    name: 'Creator',
    nameAr: 'المحترف',
    price: '$39',
    period: '/شهر',
    conversions: '150 نموذج/شهر',
    tagline: 'الأكثر طلباً للمحترفين',
    color: '#7C3AED',
    glow: 'rgba(124, 58, 237, 0.35)',
    highlight: true,
    features: [
      { text: '150 تحويل نصي-3D شهرياً', included: true },
      { text: 'رفع الصور للتوليد', included: true },
      { text: 'معاينة ثلاثية الأبعاد كاملة', included: true },
      { text: 'تحميل STL، GLB، OBJ', included: true },
      { text: 'تحسين النموذج بالذكاء الاصطناعي', included: true },
      { text: 'تاريخ النماذج (30 يوم)', included: true },
      { text: 'دعم فني أولوية', included: false },
    ],
  },
  {
    id: 'pro',
    icon: Crown,
    name: 'Pro',
    nameAr: 'المؤسسي',
    price: '$69',
    period: '/شهر',
    conversions: '500 نموذج/شهر',
    tagline: 'للفرق والشركات الكبيرة',
    color: '#EC4899',
    glow: 'rgba(236, 72, 153, 0.25)',
    features: [
      { text: '500 تحويل نصي-3D شهرياً', included: true },
      { text: 'رفع الصور للتوليد', included: true },
      { text: 'معاينة ثلاثية الأبعاد كاملة', included: true },
      { text: 'تحميل STL، GLB، OBJ، FBX', included: true },
      { text: 'تحسين النموذج غير محدود', included: true },
      { text: 'تاريخ النماذج (90 يوم)', included: true },
      { text: 'دعم فني أولوية 24/7', included: true },
    ],
  },
];

/* ── 3D Tilt Card ─────────────────────────────────────────── */
function PricingCard({ plan, delay }) {
  const cardRef = useRef(null);
  const glowRef = useRef(null);
  const Icon = plan.icon;

  /* ── Mouse tilt effect ──────────────────────────────────── */
  useEffect(() => {
    const card = cardRef.current;
    if (!card) return;

    const handleMouseMove = (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const cx = rect.width / 2;
      const cy = rect.height / 2;
      const rotX = ((y - cy) / cy) * -8;
      const rotY = ((x - cx) / cx) * 8;

      gsap.to(card, {
        rotateX: rotX,
        rotateY: rotY,
        scale: 1.03,
        duration: 0.3,
        ease: 'power2.out',
        transformPerspective: 1000,
      });

      // Move glow to cursor
      if (glowRef.current) {
        gsap.to(glowRef.current, {
          opacity: 1,
          x: x - 80,
          y: y - 80,
          duration: 0.3,
          ease: 'power2.out',
        });
      }
    };

    const handleMouseLeave = () => {
      gsap.to(card, {
        rotateX: 0,
        rotateY: 0,
        scale: 1,
        duration: 0.6,
        ease: 'elastic.out(1, 0.5)',
        transformPerspective: 1000,
      });
      if (glowRef.current) {
        gsap.to(glowRef.current, { opacity: 0, duration: 0.4 });
      }
    };

    card.addEventListener('mousemove', handleMouseMove);
    card.addEventListener('mouseleave', handleMouseLeave);
    return () => {
      card.removeEventListener('mousemove', handleMouseMove);
      card.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <div
      ref={cardRef}
      id={`pricing-${plan.id}`}
      style={{ transformStyle: 'preserve-3d', willChange: 'transform' }}
      className={`
        relative rounded-3xl overflow-hidden flex flex-col
        transition-shadow duration-300 cursor-default
        theme-card pricing-card-hover
        ${plan.highlight ? 'pricing-popular-glow border border-primary/40' : ''}
      `}
    >
      {/* Background for highlighted card */}
      {plan.highlight && (
        <div
          className="absolute inset-0 z-0"
          style={{
            background: 'linear-gradient(145deg, rgba(124,58,237,0.12) 0%, rgba(99,102,241,0.08) 100%)',
            backdropFilter: 'blur(24px)',
          }}
        />
      )}

      {/* Cursor glow */}
      <div
        ref={glowRef}
        className="absolute w-40 h-40 rounded-full pointer-events-none opacity-0 z-0"
        style={{ background: `radial-gradient(circle, ${plan.glow}, transparent 70%)` }}
      />

      {/* Most popular badge */}
      {plan.highlight && (
        <div className="absolute -top-px left-1/2 -translate-x-1/2 z-20">
          <div
            className="px-5 py-1.5 rounded-b-2xl text-xs font-bold text-white"
            style={{ background: `linear-gradient(90deg, #7C3AED, #6366F1)` }}
          >
            ⭐ الأكثر طلباً
          </div>
        </div>
      )}

      {/* Card content */}
      <div className="relative z-10 p-8 flex flex-col flex-1 mt-4">
        {/* Icon + name */}
        <div className="flex items-center gap-3 mb-6">
          <div
            className="w-12 h-12 rounded-2xl flex items-center justify-center"
            style={{ background: `${plan.color}20`, border: `1px solid ${plan.color}40` }}
          >
            <Icon size={22} style={{ color: plan.color }} />
          </div>
          <div>
            <h3 className="text-xl font-bold text-foreground">{plan.nameAr}</h3>
            <p className="text-xs text-muted-foreground">{plan.name}</p>
          </div>
        </div>

        {/* Price */}
        <div className="flex items-baseline gap-1 mb-2">
          <span className="text-5xl font-black text-foreground tracking-tight">{plan.price}</span>
          <span className="text-muted-foreground text-sm">{plan.period}</span>
        </div>
        <p className="text-sm text-muted-foreground mb-6">{plan.tagline}</p>

        {/* Conversions highlight */}
        <div
          className="flex items-center gap-2 px-4 py-2.5 rounded-2xl mb-6 text-sm font-semibold"
          style={{ background: `${plan.color}15`, border: `1px solid ${plan.color}25`, color: plan.color }}
        >
          <span
            className="w-2 h-2 rounded-full"
            style={{ background: plan.color }}
          />
          {plan.conversions}
        </div>

        {/* Divider */}
        <div className="border-t border-border mb-6" />

        {/* Feature list */}
        <ul className="space-y-3 flex-1 mb-8">
          {plan.features.map((feat, i) => (
            <li key={i} className="flex items-center gap-3 text-sm">
              {feat.included ? (
                <div
                  className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
                  style={{ background: `${plan.color}20` }}
                >
                  <Check size={11} style={{ color: plan.color }} strokeWidth={3} />
                </div>
              ) : (
                <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 bg-white/5">
                  <X size={11} className="text-white/20" strokeWidth={3} />
                </div>
              )}
              <span className={feat.included ? 'text-white/80' : 'text-white/25 line-through'}>
                {feat.text}
              </span>
            </li>
          ))}
        </ul>

        {/* CTA */}
        <button
          className={`
            w-full py-4 rounded-2xl font-bold text-base transition-all duration-200 cursor-pointer
            ${plan.highlight
              ? 'text-white hover:opacity-90'
              : 'bg-black/5 dark:bg-white/8 hover:bg-black/10 dark:hover:bg-white/15 border border-black/5 dark:border-white/10 text-foreground'}
          `}
          style={plan.highlight ? {
            background: `linear-gradient(135deg, ${plan.color}, #6366F1)`,
            boxShadow: `0 0 30px -5px ${plan.glow}`,
          } : {}}
        >
          اشترك الآن
        </button>
      </div>
    </div>
  );
}

/* ── Section ─────────────────────────────────────────────── */
export default function Pricing() {
  const sectionRef = useRef(null);

  useEffect(() => {
    const cards = sectionRef.current?.querySelectorAll('[id^="pricing-"]');
    if (!cards?.length) return;

    gsap.fromTo(
      cards,
      { opacity: 0, y: 60 },
      {
        opacity: 1,
        y: 0,
        duration: 0.8,
        stagger: 0.15,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 70%',
          once: true,
        },
      }
    );

    return () => ScrollTrigger.getAll().forEach((t) => t.kill());
  }, []);

  return (
    <section id="pricing" ref={sectionRef} className="py-24 relative max-w-5xl mx-auto px-4 sm:px-6">

      {/* Ambient blobs */}
      <div className="blob w-72 h-72 top-0 left-1/4 opacity-15"
        style={{ background: 'radial-gradient(circle, #7C3AED, transparent 70%)' }} />
      <div className="blob w-60 h-60 bottom-0 right-1/4 opacity-10"
        style={{ background: 'radial-gradient(circle, #EC4899, transparent 70%)', animationDelay: '3s' }} />

      {/* Heading */}
      <div className="text-center mb-14 relative z-10">
        <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-accent/10 border border-accent/20 text-accent text-sm font-medium mb-4">
          <Shield size={14} />
          باقات الاشتراك
        </span>
        <h2 className="text-3xl md:text-4xl font-bold mb-3">
          اختر باقتك وابدأ رحلة الإبداع
        </h2>
        <p className="text-muted-foreground text-lg max-w-xl mx-auto">
          جميع الباقات تتضمن وصولاً فورياً لتقنيات التوليد الثلاثي الأبعاد.
        </p>
      </div>

      {/* 3-column cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10 perspective-1000">
        {PLANS.map((plan, i) => (
          <PricingCard key={plan.id} plan={plan} delay={i * 0.15} />
        ))}
      </div>

      {/* Free trial note */}
      <div className="mt-12 text-center relative z-10">
        <div className="inline-flex items-center gap-3 glass border border-white/10 px-6 py-4 rounded-2xl text-sm text-muted-foreground">
          <Zap size={16} className="text-primary flex-shrink-0" />
          <span>
            جرّب مجاناً <span className="text-white font-medium">3 تحويلات</span> بدون بطاقة ائتمانية.
            المعاينة الثلاثية الأبعاد مجانية دائماً.
          </span>
        </div>
      </div>
    </section>
  );
}
