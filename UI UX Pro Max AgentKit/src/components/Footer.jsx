/**
 * Footer.jsx
 * ───────────────────────────────────────────────────────────────
 * Professional, uncrowded footer for BU3D.ai.
 *
 * Layout (4 columns on desktop):
 *  1. Brand — logo + tagline + WhatsApp
 *  2. Quick Links — About Us, T&C, Refund Policy
 *  3. Trust — Freelance document + Saudi Business Center logo
 *  4. QR Code — verify authenticity
 */

import React from 'react';
import {
  FileText, Shield, Info, MessageCircle,
  BadgeCheck, MapPin, Mail
} from 'lucide-react';

/* ── Inline SVG QR code (deterministic placeholder) ───────── */
function QRCodeSVG() {
  return (
    <svg
      width="96"
      height="96"
      viewBox="0 0 96 96"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="QR Code - امسح للتحقق"
    >
      {/* QR finder patterns */}
      <rect width="96" height="96" fill="white" />
      {/* Top-left finder */}
      <rect x="4" y="4" width="28" height="28" rx="3" fill="black" />
      <rect x="8" y="8" width="20" height="20" rx="2" fill="white" />
      <rect x="12" y="12" width="12" height="12" rx="1" fill="black" />
      {/* Top-right finder */}
      <rect x="64" y="4" width="28" height="28" rx="3" fill="black" />
      <rect x="68" y="8" width="20" height="20" rx="2" fill="white" />
      <rect x="72" y="12" width="12" height="12" rx="1" fill="black" />
      {/* Bottom-left finder */}
      <rect x="4" y="64" width="28" height="28" rx="3" fill="black" />
      <rect x="8" y="68" width="20" height="20" rx="2" fill="white" />
      <rect x="12" y="72" width="12" height="12" rx="1" fill="black" />
      {/* Data modules (deterministic pattern) */}
      {[
        [36,4],[40,4],[44,4],[48,4],[52,4],[56,4],
        [36,8],[44,8],[52,8],
        [36,12],[40,12],[44,12],[48,12],[52,12],[56,12],
        [40,16],[52,16],
        [36,20],[40,20],[48,20],[56,20],
        [36,24],[44,24],[48,24],
        [36,28],[40,28],[44,28],[52,28],[56,28],
        [4,36],[8,36],[16,36],[20,36],[28,36],[32,36],
        [36,36],[44,36],[48,36],[56,36],[60,36],[68,36],[72,36],[80,36],[84,36],[88,36],
        [4,40],[12,40],[20,40],[28,40],[36,40],[44,40],[52,40],[60,40],[68,40],[76,40],[84,40],[92,40],
        [8,44],[16,44],[24,44],[40,44],[48,44],[64,44],[72,44],[80,44],[88,44],
        [4,48],[12,48],[20,48],[28,48],[44,48],[52,48],[60,48],[76,48],[84,48],[92,48],
        [8,52],[24,52],[32,52],[40,52],[56,52],[64,52],[72,52],[88,52],
        [4,56],[12,56],[20,56],[36,56],[44,56],[52,56],[68,56],[76,56],[84,56],[92,56],
        [36,60],[40,60],[56,60],[60,60],[64,60],[72,60],[80,60],[88,60],
        [36,64],[44,64],[52,64],[60,64],[68,64],[76,64],[84,64],[92,64],
        [36,68],[40,68],[48,68],[64,68],[72,68],[80,68],[88,68],
        [36,72],[44,72],[52,72],[60,72],[76,72],[84,72],[92,72],
        [36,76],[40,76],[48,76],[56,76],[64,76],[68,76],[80,76],[88,76],
        [36,80],[44,80],[52,80],[68,80],[76,80],[84,80],[92,80],
        [36,84],[40,84],[56,84],[64,84],[72,84],[80,84],[92,84],
        [36,88],[44,88],[48,88],[52,88],[60,88],[76,88],[84,88],[92,88],
      ].map(([x, y], i) => (
        <rect key={i} x={x} y={y} width="4" height="4" fill="black" />
      ))}
    </svg>
  );
}

/* ── Saudi Business Center Logo (using existing SVG file) ── */
function SaudiBusinessBadge() {
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/8">
      {/* Logo: the SVG file exists in the project root */}
      <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center flex-shrink-0 overflow-hidden">
        <img
          src="/saudi-business-center.svg"
          alt="المركز السعودي للأعمال"
          className="w-9 h-9 object-contain"
          onError={(e) => {
            // Fallback to styled text badge
            e.target.style.display = 'none';
            e.target.parentElement.style.background = 'linear-gradient(135deg, #006C35, #00A550)';
            e.target.parentElement.innerHTML = '<span style="color:white;font-size:10px;font-weight:900;text-align:center;padding:2px;">SBC</span>';
          }}
        />
      </div>
      <div>
        <p className="text-xs font-semibold text-white leading-snug">المركز السعودي للأعمال</p>
        <p className="text-[10px] text-muted-foreground">موثق ومعتمد رسمياً</p>
      </div>
    </div>
  );
}

/* ── Freelance Document Badge ─────────────────────────────── */
function FreelanceBadge() {
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/8">
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
        style={{ background: 'linear-gradient(135deg, #7C3AED, #6366F1)' }}
      >
        <BadgeCheck className="w-5 h-5 text-white" />
      </div>
      <div>
        <p className="text-xs font-semibold text-white leading-snug">وثيقة العمل الحر</p>
        <p className="text-[10px] text-primary font-mono">767983613-FL</p>
      </div>
    </div>
  );
}

/* ── Main Footer ──────────────────────────────────────────── */
export default function Footer() {
  return (
    <footer className="border-t border-white/6 py-16 mt-8 relative overflow-hidden">

      {/* Subtle top glow */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-px"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(124,58,237,0.5), transparent)' }}
      />

      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10 lg:gap-6">

          {/* ── Column 1: Brand ─────────────────────────────── */}
          <div className="space-y-5 sm:col-span-2 lg:col-span-1">
            {/* Logo */}
            <div className="flex items-center gap-2.5">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-black text-sm"
                style={{ background: 'linear-gradient(135deg, #7C3AED, #6366F1, #EC4899)' }}
              >
                BU
              </div>
              <div>
                <span className="font-black text-xl tracking-tight text-white">BU3D</span>
                <span className="text-primary font-light">.ai</span>
              </div>
            </div>

            <p className="text-sm text-muted-foreground leading-relaxed">
              منصة الذكاء الاصطناعي الأولى لتحويل الأفكار النصية والصور إلى نماذج ثلاثية الأبعاد احترافية جاهزة للطباعة.
            </p>

            {/* WhatsApp */}
            <a
              href="https://wa.me/966511466121"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-[#25D366]/10 border border-[#25D366]/20 text-[#25D366] text-sm font-medium hover:bg-[#25D366]/20 transition-all"
            >
              <MessageCircle size={16} />
              تواصل عبر واتساب
            </a>

            {/* Location */}
            <p className="flex items-center gap-2 text-xs text-muted-foreground">
              <MapPin size={12} />
              المملكة العربية السعودية
            </p>
          </div>

          {/* ── Column 2: Quick Links ────────────────────────── */}
          <div>
            <h4 className="font-bold text-white mb-5 text-sm tracking-wide uppercase">روابط سريعة</h4>
            <ul className="space-y-3">
              {[
                { href: '#', icon: Info, label: 'من نحن' },
                { href: '#', icon: FileText, label: 'الشروط والأحكام' },
                { href: '#', icon: Shield, label: 'سياسة الاسترجاع' },
                { href: '#features', icon: null, label: 'كيف يعمل' },
                { href: '#pricing', icon: null, label: 'الأسعار' },
                { href: '#workspace', icon: null, label: 'مساحة العمل' },
              ].map((link, i) => (
                <li key={i}>
                  <a
                    href={link.href}
                    className="flex items-center gap-2.5 text-sm text-muted-foreground hover:text-white transition-colors group"
                  >
                    {link.icon && <link.icon size={13} className="group-hover:text-primary transition-colors" />}
                    {!link.icon && <span className="w-1 h-1 rounded-full bg-white/20 group-hover:bg-primary transition-colors" />}
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* ── Column 3: Trust Badges ───────────────────────── */}
          <div>
            <h4 className="font-bold text-white mb-5 text-sm tracking-wide uppercase">ثقة وأمان</h4>
            <div className="space-y-3">
              <FreelanceBadge />
              <SaudiBusinessBadge />
              <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/3 border border-white/6 text-xs text-muted-foreground">
                <Mail size={12} className="text-primary flex-shrink-0" />
                support@bu3d.ai
              </div>
            </div>
          </div>

          {/* ── Column 4: QR Code ────────────────────────────── */}
          <div>
            <h4 className="font-bold text-white mb-5 text-sm tracking-wide uppercase">تحقق من الموثوقية</h4>
            <div className="space-y-3">
              <p className="text-xs text-muted-foreground leading-relaxed">
                امسح الرمز للتحقق من هوية المنصة وضمان الأمان.
              </p>
              <div className="p-3 bg-white rounded-2xl inline-block shadow-lg">
                <QRCodeSVG />
              </div>
              <p className="text-[10px] text-muted-foreground font-mono">bu3d.ai/verify</p>
            </div>
          </div>

        </div>

        {/* ── Bottom bar ──────────────────────────────────────── */}
        <div className="mt-12 pt-6 border-t border-white/6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-xs text-muted-foreground">
            جميع الحقوق محفوظة &copy; {new Date().getFullYear()} — BU3D.ai
          </p>
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <span>مصنوع بـ</span>
            <span className="text-accent mx-1">♥</span>
            <span>في المملكة العربية السعودية</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
