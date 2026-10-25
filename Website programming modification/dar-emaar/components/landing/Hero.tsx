"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import {
  floatAnimation,
  glowPulse,
} from "@/lib/animations";
import { FileText, PhoneCall, ChevronDown } from "lucide-react";

import type { PageContent } from "@/lib/content";

export default function Hero({ 
  content, 
  heroBgImage 
}: { 
  content?: PageContent; 
  heroBgImage?: string; 
}) {
  const { scrollY } = useScroll();
  // Subtle parallax — hero content moves up slightly as user scrolls
  const y = useTransform(scrollY, [0, 500], [0, -80]);
  const activeBgImage = heroBgImage || content?.hero_bg_image;

  return (
    <section id="about" className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background: Custom banner image or default secondary background */}
      {activeBgImage ? (
        <div className="absolute inset-0 z-0 overflow-hidden">
          <img
            src={activeBgImage}
            alt="خلفية الواجهة"
            className="w-full h-full object-cover object-center scale-105 transition-transform duration-1000"
          />
          {/* Subtle contrast vignette so the photo details, lights and colors are clear */}
          <div className="absolute inset-0 bg-black/15 pointer-events-none" />
          
          {/* Balanced gradient overlay: gentle at the top and transparent in the center so the image is vibrant, then smooth fade to the next section */}
          <div className="absolute inset-0 bg-gradient-to-b from-[var(--color-secondary,#F9F3EC)]/50 via-transparent to-[var(--color-secondary,#F9F3EC)] pointer-events-none" />
          
          {/* Bottom blend buffer */}
          <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-[var(--color-secondary,#F9F3EC)] to-transparent pointer-events-none" />
        </div>
      ) : (
        <div className="absolute inset-0 bg-[var(--color-secondary)]" />
      )}
      
      {/* When no background image is set, render geometric pattern and shapes */}
      {!activeBgImage && (
        <>
          {/* Grid pattern (tech-like diagonal lines) */}
          <div
            className="absolute inset-0 opacity-[0.03] pointer-events-none"
            style={{
              backgroundImage: `repeating-linear-gradient(45deg, #6C6D71 0, #6C6D71 1px, transparent 0, transparent 50px)`,
            }}
          />

          {/* Animated glowing orbs */}
          <motion.div
            variants={glowPulse}
            animate="animate"
            className="absolute top-0 start-0 w-[500px] h-[500px] bg-[var(--color-accent)] rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none opacity-20"
          />
          <motion.div
            variants={glowPulse}
            animate="animate"
            style={{ animationDelay: "2.5s" }}
            className="absolute bottom-0 end-0 w-[500px] h-[500px] bg-[var(--color-accent)] rounded-full blur-3xl translate-x-1/3 translate-y-1/3 pointer-events-none opacity-20"
          />

          {/* Floating geometric shapes (sharp) */}
          <motion.div
            variants={floatAnimation}
            animate="animate"
            className="absolute top-1/4 end-[8%] w-20 h-20 border border-[var(--color-primary)]/20 rounded-sm rotate-12 hidden lg:block pointer-events-none"
          />
          <motion.div
            variants={floatAnimation}
            animate="animate"
            style={{ animationDelay: "1.5s" }}
            className="absolute bottom-1/3 start-[6%] w-12 h-12 border border-[var(--color-primary)]/20 rounded-sm hidden lg:block pointer-events-none"
          />
          <motion.div
            variants={floatAnimation}
            animate="animate"
            style={{ animationDelay: "3s" }}
            className="absolute top-[15%] start-[15%] w-6 h-6 bg-[var(--color-primary)]/10 rounded-sm hidden lg:block pointer-events-none"
          />
        </>
      )}

      {/* Content with parallax */}
      <motion.div
        style={{ y }}
        className="container-custom relative z-10 text-center pt-28 pb-16"
      >
        {/* Content wrapper */}
        <div className="max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2.5 bg-white/85 backdrop-blur-md border border-white/70 shadow-sm rounded-full px-5 py-2 mb-8 animate-fade-in delay-100">
            <span className="w-2.5 h-2.5 rounded-full bg-[var(--color-primary)] animate-pulse" />
            <span className="text-[var(--color-primary)] text-sm font-bold tracking-wide">
              {content?.hero_badge || "أكثر من 15 عاماً من الثقة والجودة"}
            </span>
          </div>

          {/* Main headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-[var(--color-primary)] leading-tight mb-6 drop-shadow-[0_2px_14px_rgba(255,255,255,0.85)]">
            {content?.hero_title || "شركاؤك في البناء"}
            <br />
            <span className="text-gradient drop-shadow-[0_2px_12px_rgba(255,255,255,0.7)]">
              {content?.hero_title_accent || "من الفكرة إلى التسليم"}
            </span>
          </h1>

          {/* Sub-headline */}
          <div className="mb-10 animate-fade-in-up delay-300">
            <p className="inline-block bg-white/75 backdrop-blur-md px-6 py-3 rounded-2xl border border-white/60 shadow-sm text-[#1B2A4A] text-base sm:text-lg lg:text-xl font-semibold leading-relaxed max-w-2xl mx-auto">
              {content?.hero_subtitle || "نقدم حلولاً متكاملة في المقاولات والتشطيبات وإدارة المشاريع بمعايير جودة عالية وكفاءة محترفة"}
            </p>
          </div>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12 animate-fade-in-up delay-400">
            <motion.a
              href="#contact"
              whileHover={{ scale: 1.03, y: -2 }}
              whileTap={{ scale: 0.98 }}
              className="w-full sm:w-auto bg-[var(--color-primary)] text-white px-9 py-4 rounded-xl text-lg font-bold shadow-[0_10px_25px_rgba(0,75,75,0.35)] hover:shadow-[0_16px_36px_rgba(0,75,75,0.45)] flex items-center justify-center gap-2.5 transition-all"
            >
              <FileText className="w-5 h-5" strokeWidth={2.5} />
              {content?.hero_cta || "احصل على عرض سعر مجاني"}
            </motion.a>
          </div>

          {/* Phone number */}
          <div className="animate-fade-in delay-500">
            <motion.a
              href="tel:+966500000000"
              whileHover={{ scale: 1.04 }}
              className="inline-flex items-center gap-3 bg-white/80 hover:bg-white backdrop-blur-md px-6 py-2.5 rounded-full border border-white/70 shadow-sm hover:shadow-md text-[var(--color-primary)] transition-all group"
            >
              <div className="w-9 h-9 rounded-full bg-[var(--color-primary)]/10 group-hover:bg-[var(--color-primary)]/20 flex items-center justify-center text-[var(--color-primary)] transition-colors">
                <PhoneCall className="w-4 h-4" strokeWidth={2.5} />
              </div>
              <span className="font-bold text-base sm:text-lg text-[var(--color-primary)]" dir="ltr">
                {content?.phone_number || "+966 50 000 0000"}
              </span>
              <span className="text-xs sm:text-sm text-[#475569] font-medium">
                — {content?.hero_phone_label || "تحدث مع الفريق الهندسي"}
              </span>
            </motion.a>
          </div>
        </div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.8, duration: 0.6 }}
        className="absolute bottom-8 inset-x-0 flex justify-center z-10"
      >
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
        >
          <ChevronDown className="w-6 h-6 text-[var(--color-primary)]/40" strokeWidth={2.5} />
        </motion.div>
      </motion.div>
    </section>
  );
}
