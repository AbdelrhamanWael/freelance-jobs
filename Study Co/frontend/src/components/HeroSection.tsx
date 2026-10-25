'use client';

import { useTranslation } from 'react-i18next';
import { MessageCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export default function HeroSection() {
  const { i18n } = useTranslation();
  const isRtl = i18n.language === 'ar';

  const features = isRtl
    ? [
        { icon: '💬', label: 'استشارة مجانية' },
        { icon: '🛡', label: 'فريق ذو خبرة' },
        { icon: '❤️', label: 'دعم متكامل' },
      ]
    : [
        { icon: '💬', label: 'Konsultasi Gratis' },
        { icon: '👥', label: 'Tim Berpengalaman' },
        { icon: '✅', label: 'Proses Mudah & Aman' },
        { icon: '❤️', label: 'Dukungan Penuh' },
      ];

  return (
    <section className="relative overflow-hidden bg-[#f7f8fc]" style={{ minHeight: '480px' }}>

      {/* ── FULL-WIDTH BACKGROUND IMAGE ── */}
      <div className="absolute inset-0">
        <img
          src="https://images.unsplash.com/photo-1539635278303-d4002c07eae3?w=1600&q=90&fit=crop&crop=center"
          alt="Student traveler"
          className="w-full h-full object-cover"
        />
        {/*
          Gradient overlay:
          - LTR: heavy white on LEFT (text side), transparent on RIGHT (image side)
          - RTL: heavy white on RIGHT (text side), transparent on LEFT (image side)
        */}
        {isRtl ? (
          <div
            className="absolute inset-0"
            style={{
              background: 'linear-gradient(to left, rgba(247,248,252,0.97) 0%, rgba(247,248,252,0.95) 35%, rgba(247,248,252,0.7) 55%, rgba(247,248,252,0.1) 75%, transparent 100%)',
            }}
          />
        ) : (
          <div
            className="absolute inset-0"
            style={{
              background: 'linear-gradient(to right, rgba(247,248,252,0.97) 0%, rgba(247,248,252,0.95) 35%, rgba(247,248,252,0.7) 55%, rgba(247,248,252,0.1) 75%, transparent 100%)',
            }}
          />
        )}
      </div>

      {/* Airplane icon */}
      <div className="absolute top-10 left-1/2 -translate-x-1/2 text-yellow text-2xl z-10 opacity-90">
        ✈
      </div>

      {/* ── CONTENT WRAPPER ── */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 sm:px-10 lg:px-8 pt-14 pb-32 sm:pb-14 lg:py-20 min-h-[480px] flex items-center">

        {/*
          Text block:
          - LTR: aligned to the LEFT
          - RTL: aligned to the RIGHT (HTML dir="rtl" handles this naturally)
        */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
          className="w-full lg:w-[48%]"
        >
          {/* Headline */}
          {isRtl ? (
            <h1 className="text-4xl lg:text-5xl font-black text-gray-900 leading-tight">
              مستقبلك يبدأ الآن
              <br />
              <span className="text-yellow">مع StudyCo</span>
            </h1>
          ) : (
            <h1 className="text-4xl lg:text-5xl font-black text-gray-900 leading-tight">
              Masa Depanmu Dimulai{' '}
              <span className="text-yellow">Sekarang</span>
              <br />
              bersama <span className="text-yellow">StudyCo</span>
            </h1>
          )}

          {/* Subtitle */}
          <p className="text-gray-600 mt-4 mb-6 text-[15px] leading-relaxed">
            {isRtl
              ? 'نساعد الطلاب الإندونيسيين على تحقيق أحلامهم الدراسية من خلال الجامعات والمعاهد والبرامج العالمية الموثوقة.'
              : 'Kami membantu pelajar Indonesia meraih pendidikan terbaik di universitas, institusi bahasa, dan program online berkualitas di seluruh dunia.'}
          </p>

          {/* Feature badges */}
          <div className="flex flex-wrap gap-x-5 gap-y-2 mb-8">
            {features.map((f) => (
              <span key={f.label} className="flex items-center gap-1.5 text-sm font-medium text-gray-600">
                <span>{f.icon}</span>{f.label}
              </span>
            ))}
          </div>

          {/* CTA */}
          <div className="flex flex-col gap-2">
            <a
              href="https://wa.me/1234567890"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-3 bg-yellow hover:bg-yellow-dark text-white font-bold text-base px-7 py-3.5 rounded-full shadow-lg shadow-yellow/30 transition-all hover:-translate-y-0.5 w-fit"
            >
              <MessageCircle className="w-5 h-5 flex-shrink-0" />
              {isRtl ? 'تواصل معنا الآن عبر واتساب' : 'Hubungi Kami di WhatsApp'}
            </a>
            <p className="text-xs text-gray-400">
              {isRtl ? 'رد سريع ومعلومات كاملة' : 'Respon cepat • Informasi lengkap • 100% Gratis'}
            </p>
          </div>
        </motion.div>
      </div>

      {/* ── TRUST BADGE ── hidden on mobile to prevent button overlap */}
      <div
        className={`absolute bottom-8 z-20 hidden sm:block ${isRtl ? 'left-6 sm:left-10' : 'right-6 sm:right-10'}`}
      >
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl px-5 py-4 flex items-center gap-3 border border-gray-100">
          <div className="w-11 h-11 rounded-full bg-yellow/15 flex items-center justify-center text-xl flex-shrink-0">
            👥
          </div>
          <div>
            <p className="font-black text-gray-900 text-sm">
              {isRtl ? 'آلاف الطلاب' : 'Ribuan Pelajar'}
            </p>
            <p className="text-xs text-gray-500 mt-0.5">
              {isRtl ? 'حققوا أحلامهم معنا' : 'Telah percaya pada kami'}
            </p>
            <div className="flex items-center gap-1 mt-1 text-yellow text-xs">
              ★★★★★
              <span className="text-gray-900 font-bold ms-1">4.9</span>
            </div>
          </div>
        </div>
      </div>

    </section>
  );
}
