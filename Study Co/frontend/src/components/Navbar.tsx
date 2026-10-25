'use client';

import { useTranslation } from 'react-i18next';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useState } from 'react';
import { ChevronDown, Menu, X, MessageCircle, Globe } from 'lucide-react';

const NAV_ITEMS_AR = [
  { label: 'الرئيسية', href: '/' },
  { label: 'خدمات الطلاب', href: '#student-services', hasDropdown: true },
  { label: 'الدرجات الجامعية أونلاين', href: '#online-degrees', hasDropdown: true },
  { label: 'الدرجات الجامعية', href: '#degrees', hasDropdown: true },
  { label: 'الدراسة في الخارج', href: '#destinations', hasDropdown: true },
];

const NAV_ITEMS_ID = [
  { label: 'Beranda', href: '/' },
  { label: 'Belajar di Luar Negeri', href: '#destinations', hasDropdown: true },
  { label: 'Belajar Bahasa Inggris', href: '#english', hasDropdown: true },
  { label: 'Gelar Online', href: '#online-degrees', hasDropdown: true },
  { label: 'Layanan Mahasiswa', href: '#student-services', hasDropdown: true },
  { label: 'Tentang Kami', href: '#about', hasDropdown: true },
];

export default function Navbar() {
  const { i18n } = useTranslation();
  const isRtl = i18n.language === 'ar';
  const currentLocale = i18n.language;
  const router = useRouter();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = isRtl ? NAV_ITEMS_AR : NAV_ITEMS_ID;

  const switchLocale = () => {
    const newLocale = isRtl ? 'id' : 'ar';
    const newPath = pathname.replace(`/${currentLocale}`, `/${newLocale}`);
    router.push(newPath);
    router.refresh();
  };

  const ctaLabel = isRtl ? 'استشارة مجانية' : 'Konsultasi Gratis';

  return (
    <>
      <header className="sticky top-0 z-50 bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">

            {/* ── LOGO ── */}
            <Link href={`/${currentLocale}`} className="flex flex-col leading-none flex-shrink-0">
              <span className="text-[22px] font-extrabold tracking-tight text-gray-900">
                Study<span className="text-yellow">Co</span>
              </span>
              <span className="text-[7px] font-semibold tracking-[2.5px] text-gray-400 uppercase">
                Education Services
              </span>
            </Link>

            {/* ── DESKTOP NAV ── */}
            <nav className="hidden lg:flex items-center gap-5 xl:gap-7">
              {navItems.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className="flex items-center gap-1 text-sm font-medium text-gray-700 hover:text-yellow transition-colors whitespace-nowrap"
                >
                  {item.label}
                  {item.hasDropdown && <ChevronDown className="w-3 h-3 opacity-50" />}
                </a>
              ))}
            </nav>

            {/* ── RIGHT SIDE: Lang + CTA + Hamburger ── */}
            <div className="flex items-center gap-2 sm:gap-3">

              {/* Language Switcher */}
              <button
                onClick={switchLocale}
                className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-yellow transition-colors border border-gray-200 hover:border-yellow rounded-full px-3 py-1.5"
              >
                <Globe className="w-3.5 h-3.5" />
                {isRtl ? 'Indonesia' : 'عربي'}
              </button>

              {/* CTA Button */}
              <a
                href="https://wa.me/1234567890"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 bg-yellow hover:bg-yellow-dark text-white text-xs sm:text-sm font-bold px-3 sm:px-4 py-2 sm:py-2.5 rounded-lg transition-all hover:-translate-y-0.5 shadow-md shadow-yellow/25 whitespace-nowrap"
              >
                <MessageCircle className="w-4 h-4" />
                <span className="hidden xs:inline">{ctaLabel}</span>
                <span className="xs:hidden">WhatsApp</span>
              </a>

              {/* Hamburger (mobile only) */}
              <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
                aria-label="Toggle menu"
              >
                {mobileOpen
                  ? <X className="w-5 h-5 text-gray-700" />
                  : <Menu className="w-5 h-5 text-gray-700" />
                }
              </button>
            </div>

          </div>
        </div>
      </header>

      {/* ── MOBILE MENU OVERLAY ── */}
      {mobileOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/30 z-40 lg:hidden"
            onClick={() => setMobileOpen(false)}
          />

          {/* Slide-in panel */}
          <div className="fixed top-0 bottom-0 z-50 lg:hidden bg-white shadow-2xl w-72 flex flex-col"
            style={{ [isRtl ? 'right' : 'left']: 0 }}
          >
            {/* Panel Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
              <div className="flex flex-col leading-none">
                <span className="text-xl font-extrabold tracking-tight text-gray-900">
                  Study<span className="text-yellow">Co</span>
                </span>
                <span className="text-[7px] font-semibold tracking-[2px] text-gray-400 uppercase">
                  Education Services
                </span>
              </div>
              <button
                onClick={() => setMobileOpen(false)}
                className="p-2 rounded-lg hover:bg-gray-100"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            {/* Nav Links */}
            <nav className="flex-1 overflow-y-auto py-4 px-5">
              <ul className="space-y-1">
                {navItems.map((item) => (
                  <li key={item.label}>
                    <a
                      href={item.href}
                      onClick={() => setMobileOpen(false)}
                      className="flex items-center justify-between py-3 px-3 rounded-xl text-sm font-medium text-gray-700 hover:bg-yellow/10 hover:text-yellow transition-colors"
                    >
                      {item.label}
                      {item.hasDropdown && <ChevronDown className="w-4 h-4 opacity-40" />}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>

            {/* Panel Footer: Language switcher + CTA */}
            <div className="px-5 py-5 border-t border-gray-100 space-y-3">
              <button
                onClick={() => { switchLocale(); setMobileOpen(false); }}
                className="flex items-center justify-center gap-2 w-full text-sm font-semibold text-gray-600 border border-gray-200 rounded-xl py-2.5 hover:border-yellow hover:text-yellow transition-colors"
              >
                <Globe className="w-4 h-4" />
                {isRtl ? 'Switch to Indonesia' : 'التبديل إلى العربية'}
              </button>
              <a
                href="https://wa.me/1234567890"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setMobileOpen(false)}
                className="flex items-center justify-center gap-2 w-full bg-yellow hover:bg-yellow-dark text-white font-bold text-sm py-3 rounded-xl transition-all shadow-md shadow-yellow/25"
              >
                <MessageCircle className="w-4 h-4" />
                {ctaLabel}
              </a>
            </div>
          </div>
        </>
      )}
    </>
  );
}
