"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import type { BlogPost } from "@/lib/db-blogs";
import type { SiteSettings } from "@/lib/settings";
import { fadeInUp, staggerContainer } from "@/lib/animations";

type Props = {
  post: BlogPost;
  relatedPosts: BlogPost[];
  settings: SiteSettings;
};

export default function BlogDetail({ post, relatedPosts, settings }: Props) {
  const [copied, setCopied] = useState(false);
  const [currentUrl, setCurrentUrl] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      setCurrentUrl(window.location.href);
    }
  }, []);

  // Calculate estimated reading time
  const wordCount = (post.content || "").replace(/<[^>]*>/g, "").trim().split(/\s+/).length;
  const readTimeMinutes = Math.max(1, Math.ceil(wordCount / 180));

  // Formatted date in Arabic
  const formattedDate = post.created_at
    ? new Date(post.created_at).toLocaleDateString("ar-SA", {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : "";

  // Check if image URL is a valid web image
  const isValidCover =
    post.cover_image &&
    !post.cover_image.startsWith("file:") &&
    (post.cover_image.startsWith("http://") ||
      post.cover_image.startsWith("https://") ||
      post.cover_image.startsWith("/"));

  const handleCopyLink = () => {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(currentUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const whatsappShareUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(
    `${post.title}\n${currentUrl}`
  )}`;
  const twitterShareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(
    post.title
  )}&url=${encodeURIComponent(currentUrl)}`;

  return (
    <main className="min-h-screen bg-[var(--color-secondary,#F9F3EC)]">
      {/* ── Top Hero Section ── */}
      <section className="relative pt-32 pb-20 bg-[var(--color-primary,#004B4B)] overflow-hidden">
        {/* Ambient background glow & grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.05] pointer-events-none"
          style={{
            backgroundImage: `repeating-linear-gradient(45deg, #fff 0, #fff 1px, transparent 0, transparent 40px)`,
          }}
        />
        <motion.div
          animate={{ scale: [1, 1.15, 1], opacity: [0.08, 0.15, 0.08] }}
          transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-0 end-0 w-96 h-96 bg-white/20 rounded-full blur-3xl pointer-events-none"
        />

        <div className="container-custom relative z-10">
          {/* Breadcrumbs */}
          <motion.nav
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="flex items-center gap-2 text-white/60 text-xs sm:text-sm mb-6 flex-wrap"
          >
            <Link href="/" className="hover:text-white transition-colors">
              الرئيسية
            </Link>
            <span className="text-white/40">/</span>
            <Link href="/blog" className="hover:text-white transition-colors">
              المدونة
            </Link>
            <span className="text-white/40">/</span>
            <span className="text-white/90 font-medium truncate max-w-[200px] sm:max-w-xs">
              {post.title}
            </span>
          </motion.nav>

          <motion.div
            variants={staggerContainer(0.1, 0.05)}
            initial="hidden"
            animate="visible"
            className="max-w-4xl"
          >
            {/* Tags */}
            <motion.div variants={fadeInUp} className="flex flex-wrap gap-2 mb-4">
              <span className="px-3 py-1 text-xs font-bold rounded-sm bg-white/15 text-white border border-white/20">
                مدونة دار اعمار
              </span>
              {post.tags &&
                post.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2.5 py-1 text-xs font-semibold rounded-sm bg-white/10 text-white/80"
                  >
                    {tag}
                  </span>
                ))}
            </motion.div>

            {/* Title */}
            <motion.h1
              variants={fadeInUp}
              className="text-3xl sm:text-4xl md:text-5xl font-black text-white leading-tight mb-6"
            >
              {post.title}
            </motion.h1>

            {/* Meta Bar */}
            <motion.div
              variants={fadeInUp}
              className="flex flex-wrap items-center gap-4 sm:gap-6 text-xs sm:text-sm text-white/75 pt-2 border-t border-white/10"
            >
              {/* Author */}
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-full bg-white p-1 flex items-center justify-center flex-shrink-0 shadow-sm overflow-hidden">
                  <Image
                    src="/Logo-daremmar.png"
                    alt="دار اعمار الغربية"
                    width={32}
                    height={32}
                    className="w-full h-full object-contain"
                  />
                </div>
                <span>{post.author || "فريق دار اعمار الغربية"}</span>
              </div>

              {/* Date */}
              {formattedDate && (
                <div className="flex items-center gap-1.5">
                  <svg className="w-4 h-4 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>{formattedDate}</span>
                </div>
              )}

              {/* Reading time */}
              <div className="flex items-center gap-1.5">
                <svg className="w-4 h-4 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>قراءة {readTimeMinutes} دقيقة</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ── Main Content Area ── */}
      <div className="container-custom py-12 md:py-16">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
          
          {/* ──── Left/Center: Article Content (8 cols) ──── */}
          <article className="lg:col-span-8 space-y-8">
            {/* Featured Image */}
            <div className="relative w-full aspect-[16/9] sm:aspect-[21/9] rounded-2xl overflow-hidden shadow-md bg-gradient-to-br from-[#004B4B] to-[#043333] border border-[var(--color-accent)]/15">
              {isValidCover ? (
                <img
                  src={post.cover_image}
                  alt={post.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center p-8 text-center bg-gradient-to-br from-[#004B4B] via-[#003838] to-[#032929] text-white">
                  <div className="w-16 h-16 rounded-2xl bg-white/10 flex items-center justify-center mb-4 border border-white/15">
                    <svg className="w-8 h-8 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                  </div>
                  <span className="text-xs uppercase tracking-widest text-white/60 mb-1 font-semibold">
                    دار اعمار الغربية للمقاولات
                  </span>
                  <h3 className="text-xl sm:text-2xl font-bold text-white max-w-md">
                    {post.title}
                  </h3>
                </div>
              )}
            </div>

            {/* Excerpt callout */}
            {post.excerpt && (
              <div className="bg-white border-r-4 border-[var(--color-primary)] p-6 rounded-xl shadow-sm text-lg leading-relaxed text-[#1B2A4A] font-medium">
                {post.excerpt}
              </div>
            )}

            {/* Main Content Body */}
            <div className="bg-white rounded-2xl p-6 sm:p-10 shadow-sm border border-[#E2E8F0] space-y-6">
              {post.content ? (
                <div
                  className="prose prose-lg max-w-none text-[#334155] leading-loose text-base sm:text-lg article-html-content"
                  style={{ color: "#334155" }}
                  dangerouslySetInnerHTML={{
                    __html: post.content.includes("<")
                      ? post.content
                      : post.content.split("\n").map(p => `<p class="mb-4">${p}</p>`).join(""),
                  }}
                />
              ) : (
                <p className="text-gray-500 text-center py-8">لا يوجد محتوى إضافي لهذا المقال.</p>
              )}
            </div>

            {/* ── Share Bar ── */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#E2E8F0] flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2 text-sm font-bold text-[var(--color-primary)]">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
                <span>شارك المقال مع أصدقائك:</span>
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                {/* WhatsApp */}
                <a
                  href={whatsappShareUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-[#25D366]/10 text-[#128C7E] hover:bg-[#25D366] hover:text-white transition-all text-xs sm:text-sm font-bold"
                >
                  <svg className="w-4 h-4 fill-currentColor" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347zM12 0C5.373 0 0 5.373 0 12c0 2.124.554 4.122 1.528 5.858L0 24l6.336-1.508A11.93 11.93 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.818a9.8 9.8 0 01-5.004-1.373l-.36-.213-3.76.896.952-3.653-.235-.375A9.79 9.79 0 012.182 12C2.182 6.58 6.58 2.182 12 2.182S21.818 6.58 21.818 12 17.42 21.818 12 21.818z"/>
                  </svg>
                  <span>واتساب</span>
                </a>

                {/* Twitter / X */}
                <a
                  href={twitterShareUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-gray-100 text-gray-800 hover:bg-black hover:text-white transition-all text-xs sm:text-sm font-bold"
                >
                  <svg className="w-4 h-4 fill-currentColor" viewBox="0 0 24 24">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                  </svg>
                  <span>منصة X</span>
                </a>

                {/* Copy Link Button */}
                <button
                  onClick={handleCopyLink}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-[var(--color-primary)]/10 text-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-white transition-all text-xs sm:text-sm font-bold"
                >
                  {copied ? (
                    <>
                      <svg className="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>تم النسخ!</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      <span>نسخ الرابط</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* ── Author Box ── */}
            <div className="bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-[#E2E8F0] flex flex-col sm:flex-row items-center sm:items-start gap-5 text-center sm:text-right">
              <div className="w-16 h-16 rounded-2xl bg-[var(--color-secondary,#F9F3EC)] border border-[var(--color-primary)]/15 p-2 flex items-center justify-center flex-shrink-0 shadow-sm overflow-hidden">
                <Image
                  src="/Logo-daremmar.png"
                  alt="دار اعمار الغربية"
                  width={64}
                  height={64}
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="space-y-1 flex-1">
                <h4 className="text-lg font-bold text-[var(--color-primary)]">
                  {post.author || "فريق دار اعمار الغربية"}
                </h4>
                <p className="text-xs text-[var(--color-accent)] font-semibold">
                  {post.author_title || "قسم الهندسة والمحتوى المعماري"}
                </p>
                <p className="text-sm text-gray-600 leading-relaxed pt-1">
                  {post.author_bio || "نشارككم خبراتنا الميدانية وأحدث الأفكار والحلول الهندسية في مجالات المقاولات العامة والتشطيبات الفاخرة وإدارة المشاريع بالمملكة العربية السعودية."}
                </p>
              </div>
            </div>

            {/* Back to Blog link */}
            <div className="pt-4 flex justify-between items-center">
              <Link
                href="/blog"
                className="inline-flex items-center gap-2 text-[var(--color-primary)] font-bold text-sm hover:underline"
              >
                <svg className="w-4 h-4 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                العودة لجميع المقالات
              </Link>
              <Link
                href="/"
                className="text-xs text-[var(--color-accent)] hover:text-[var(--color-primary)] font-semibold"
              >
                الصفحة الرئيسية
              </Link>
            </div>
          </article>

          {/* ──── Right: Sticky Sidebar (4 cols) ──── */}
          <aside className="lg:col-span-4 space-y-6 lg:sticky lg:top-28">
            
            {/* CTA Consultation Card */}
            <div className="bg-[var(--color-primary)] text-white rounded-2xl p-6 sm:p-7 shadow-lg relative overflow-hidden">
              <div className="absolute top-0 left-0 w-32 h-32 bg-white/5 rounded-full blur-2xl pointer-events-none" />
              <span className="inline-block px-3 py-1 bg-white/10 rounded-sm text-xs font-bold text-white/90 mb-4">
                استشارة هندسية مجانية
              </span>
              <h3 className="text-xl font-black mb-3 leading-snug">
                هل تخطط لمشروع تشطيبات أو مقاولات؟
              </h3>
              <p className="text-white/80 text-sm leading-relaxed mb-6">
                تواصل مع خبرائنا في شركة دار اعمار الغربية للحصول على تقييم هندسي وعرض سعر مخصص لمشروعك.
              </p>

              <div className="space-y-3">
                <a
                  href={settings.whatsapp || "https://wa.me/966500000000"}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full py-3 px-4 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-sm shadow transition-all duration-200"
                >
                  <svg className="w-5 h-5 fill-currentColor" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347zM12 0C5.373 0 0 5.373 0 12c0 2.124.554 4.122 1.528 5.858L0 24l6.336-1.508A11.93 11.93 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.818a9.8 9.8 0 01-5.004-1.373l-.36-.213-3.76.896.952-3.653-.235-.375A9.79 9.79 0 012.182 12C2.182 6.58 6.58 2.182 12 2.182S21.818 6.58 21.818 12 17.42 21.818 12 21.818z"/>
                  </svg>
                  <span>محادثة واتساب فورية</span>
                </a>

                <Link
                  href="/#contact"
                  className="flex items-center justify-center gap-2 w-full py-3 px-4 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm border border-white/20 transition-all duration-200"
                >
                  <span>طلب استشارة عبر الموقع</span>
                </Link>
              </div>
            </div>

            {/* Quick Company Info */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#E2E8F0] space-y-4 text-sm">
              <h4 className="font-bold text-[var(--color-primary)] pb-2 border-b border-[#E2E8F0]">
                تواصل مع دار اعمار الغربية
              </h4>
              {settings.phone && (
                <div className="flex items-center gap-3 text-gray-700">
                  <span className="w-8 h-8 rounded-lg bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center flex-shrink-0">
                    📞
                  </span>
                  <span dir="ltr" className="font-semibold">{settings.phone}</span>
                </div>
              )}
              {settings.contact_email && (
                <div className="flex items-center gap-3 text-gray-700">
                  <span className="w-8 h-8 rounded-lg bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center flex-shrink-0">
                    ✉️
                  </span>
                  <span className="truncate">{settings.contact_email}</span>
                </div>
              )}
              {settings.working_hours && (
                <div className="flex items-center gap-3 text-gray-700">
                  <span className="w-8 h-8 rounded-lg bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center flex-shrink-0">
                    🕒
                  </span>
                  <span>{settings.working_hours}</span>
                </div>
              )}
            </div>

            {/* Recent Blogs Widget in Sidebar */}
            {relatedPosts.length > 0 && (
              <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#E2E8F0] space-y-4">
                <h4 className="font-bold text-[var(--color-primary)] pb-2 border-b border-[#E2E8F0] flex items-center justify-between">
                  <span>أحدث المقالات</span>
                  <Link href="/blog" className="text-xs text-[var(--color-primary)] hover:underline">
                    عرض الكل
                  </Link>
                </h4>
                <div className="space-y-4">
                  {relatedPosts.slice(0, 3).map((item) => (
                    <Link
                      key={item.id}
                      href={`/blog/${item.slug}`}
                      className="group flex gap-3 items-start"
                    >
                      <div className="w-16 h-16 rounded-xl overflow-hidden bg-gray-100 flex-shrink-0 relative border border-gray-200">
                        {item.cover_image && !item.cover_image.startsWith("file:") ? (
                          <img
                            src={item.cover_image}
                            alt={item.title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center bg-[var(--color-primary)]/10 text-[var(--color-primary)] text-xs font-bold">
                            دار اعمار
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h5 className="text-xs font-bold text-gray-900 group-hover:text-[var(--color-primary)] transition-colors line-clamp-2 leading-relaxed">
                          {item.title}
                        </h5>
                        <p className="text-[11px] text-gray-400 mt-1">
                          {item.created_at ? new Date(item.created_at).toLocaleDateString("ar-SA") : ""}
                        </p>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            )}

          </aside>
        </div>

        {/* ──── Bottom Section: Related Articles (Grid of 3) ──── */}
        {relatedPosts.length > 0 && (
          <section className="mt-20 pt-12 border-t border-[var(--color-accent)]/15">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h3 className="text-2xl font-black text-[var(--color-primary)]">مقالات أخرى قد تهمك</h3>
                <p className="text-sm text-[var(--color-accent)] mt-1">
                  اكتشف المزيد من المقالات والأفكار في عالم المقاولات والتصميم الداخلي
                </p>
              </div>
              <Link
                href="/blog"
                className="hidden sm:inline-flex items-center gap-1.5 text-sm font-bold text-[var(--color-primary)] hover:underline"
              >
                عرض جميع المقالات
                <svg className="w-4 h-4 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {relatedPosts.map((rPost) => (
                <Link
                  key={rPost.id}
                  href={`/blog/${rPost.slug}`}
                  className="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col border border-[var(--color-accent)]/10"
                >
                  <div className="relative h-48 w-full overflow-hidden bg-gray-100">
                    {rPost.cover_image && !rPost.cover_image.startsWith("file:") ? (
                      <img
                        src={rPost.cover_image}
                        alt={rPost.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#004B4B]/15 to-[#004B4B]/5 text-[var(--color-primary)]">
                        <svg className="w-10 h-10 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                        </svg>
                      </div>
                    )}
                  </div>
                  <div className="p-5 flex flex-col flex-1">
                    <p className="text-xs font-bold text-[var(--color-accent)] mb-2">
                      {rPost.created_at
                        ? new Date(rPost.created_at).toLocaleDateString("ar-SA", {
                            year: "numeric",
                            month: "long",
                            day: "numeric",
                          })
                        : ""}
                    </p>
                    <h4 className="text-base font-bold text-[var(--color-primary)] mb-2 line-clamp-2 group-hover:text-[#003838]">
                      {rPost.title}
                    </h4>
                    {rPost.excerpt && (
                      <p className="text-xs text-[var(--color-accent)] line-clamp-2 mb-4">
                        {rPost.excerpt}
                      </p>
                    )}
                    <div className="mt-auto flex items-center text-[var(--color-primary)] font-bold text-xs gap-1 group-hover:gap-2 transition-all">
                      <span>اقرأ المقال</span>
                      <svg className="w-3.5 h-3.5 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
