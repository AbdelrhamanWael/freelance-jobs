"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import LanguageSwitcher from "./LanguageSwitcher";

const baseNavLinks = [
  { href: "/#about", label: "من نحن" },
  { href: "/#services", label: "خدماتنا" },
  { href: "/projects", label: "مشاريعنا" },
  { href: "/#clients", label: "عملاؤنا" },
  { href: "/#contact", label: "اتصل بنا" },
];
export default function Navbar({ 
  isBlogEnabled = false,
  headerCtaText = "طلب استشارة",
  logoUrl,
}: { 
  isBlogEnabled?: boolean;
  headerCtaText?: string;
  logoUrl?: string;
}) {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  // Add blog link if enabled
  const navLinks = isBlogEnabled
    ? [...baseNavLinks, { href: "/blog", label: "المدونة" }]
    : baseNavLinks;

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-[var(--color-secondary)]/95 backdrop-blur-md shadow-md py-2"
          : "bg-[var(--color-secondary)]/80 backdrop-blur-md py-3.5 border-b border-black/[0.03]"
      }`}
    >
      <div className="container-custom flex items-center justify-between gap-4">

        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 flex-shrink-0">
          <Image 
            src={logoUrl || "/logo-horizontal.png"} 
            alt="دار اعمار الغربية" 
            width={220} 
            height={64} 
            className="object-contain h-12 w-auto sm:h-14 md:h-16 transition-all duration-300" 
            priority
            unoptimized={Boolean(logoUrl && logoUrl.startsWith("http"))}
          />
        </Link>

        {/* Desktop nav */}
        <nav className="hidden lg:flex items-center gap-7">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-[var(--color-accent)] hover:text-[var(--color-primary)] font-medium text-[0.95rem] transition-colors duration-200 relative group"
            >
              {link.label}
              <span className="absolute -bottom-1 start-0 w-0 h-0.5 bg-[var(--color-primary)] group-hover:w-full transition-all duration-300 rounded-none" />
            </a>
          ))}
        </nav>

        {/* Desktop CTAs & Lang */}
        <div className="hidden lg:flex items-center gap-3">
          <LanguageSwitcher />
          <a
            href="/#contact"
            className="bg-[var(--color-primary)] hover:bg-[var(--color-primary)]/90 text-white px-6 py-2.5 rounded-sm text-sm font-bold transition-all duration-200 shadow-[0_4px_14px_rgba(0,75,75,0.35)] hover:shadow-[0_4px_20px_rgba(0,75,75,0.5)] hover:-translate-y-px active:translate-y-0"
          >
            {headerCtaText}
          </a>
        </div>

        {/* Mobile menu button */}
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="lg:hidden text-[var(--color-primary)] p-2 rounded-lg hover:bg-[var(--color-primary)]/10 transition-colors"
          aria-label="فتح القائمة"
        >
          {menuOpen ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          )}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="lg:hidden bg-[var(--color-secondary)]/98 backdrop-blur-md border-t border-[var(--color-accent)]/10 px-5 py-4 space-y-1 shadow-lg">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setMenuOpen(false)}
              className="block text-[var(--color-accent)] hover:text-[var(--color-primary)] font-medium py-3 border-b border-[var(--color-accent)]/10 transition-colors"
            >
              {link.label}
            </a>
          ))}
          <div className="flex items-center gap-3 pt-4">
            <LanguageSwitcher />
            <a
              href="/#contact"
              onClick={() => setMenuOpen(false)}
              className="flex-1 bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary)]/90 text-center py-3 rounded-sm font-bold text-sm shadow-[0_4px_14px_rgba(0,75,75,0.35)]"
            >
              {headerCtaText}
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
