"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import type { DbProject } from "@/lib/db-projects";
import { fadeInUp, fadeInLeft, fadeInRight, staggerContainer, scaleIn } from "@/lib/animations";
import type { PageContent } from "@/lib/content";

type Props = { 
  project: DbProject;
  content: PageContent;
};

const META_ICONS: Record<string, React.ReactElement> = {
  location: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  ),
  client: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5" />
    </svg>
  ),
  duration: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  year: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  ),
};

export default function ProjectDetail({ project, content }: Props) {
  const images = (project.images || []).filter((s) => s && !s.startsWith("file:"));
  const [activeImageIndex, setActiveImageIndex] = React.useState(0);
  const activeImage = images[activeImageIndex] || images[0] || null;

  return (
    <main className="min-h-screen bg-[var(--color-secondary)]">

        {/* Hero banner */}
        <div className="relative bg-[var(--color-primary)] pt-24 pb-16 overflow-hidden">
          {/* Background decorations */}
          <motion.div
            animate={{ scale: [1, 1.2, 1], opacity: [0.05, 0.1, 0.05] }}
            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            className="absolute top-0 end-0 w-96 h-96 bg-[var(--color-secondary)] rounded-sm blur-3xl translate-x-1/2 -translate-y-1/2 pointer-events-none"
          />
          <div className="container-custom relative z-10">
            {/* Back breadcrumb */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4 }}
            >
              <Link
                href="/"
                className="inline-flex items-center gap-2 text-white/50 hover:text-[var(--color-secondary)] text-sm transition-colors mb-8 group"
              >
                <svg className="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                العودة للرئيسية
              </Link>
            </motion.div>

            {/* Project title */}
            <motion.div
              variants={staggerContainer(0.15)}
              initial="hidden"
              animate="visible"
              className="space-y-4 max-w-3xl"
            >
              <div className="flex flex-wrap items-center gap-3">
                {project.category && (
                  <motion.span
                    variants={fadeInUp}
                    className="inline-block text-xs font-semibold px-3 py-1 rounded-sm uppercase tracking-wider"
                    style={{
                      background: "rgba(249, 243, 236, 0.12)",
                      color: "var(--color-secondary)",
                      border: "1px solid rgba(249, 243, 236, 0.2)",
                    }}
                  >
                    {project.category.name}
                  </motion.span>
                )}
                {project.is_featured && (
                  <motion.span
                    variants={fadeInUp}
                    className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-sm"
                    style={{
                      background: "rgba(201, 162, 39, 0.2)",
                      color: "var(--color-secondary)",
                      border: "1px solid rgba(201, 162, 39, 0.35)",
                    }}
                  >
                    <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                    مشروع مميز
                  </motion.span>
                )}
              </div>

              <motion.h1
                variants={fadeInUp}
                className="text-3xl md:text-5xl font-black text-white leading-tight"
              >
                {project.title}
              </motion.h1>

              {project.description && (
                <motion.p
                  variants={fadeInUp}
                  className="text-white/70 text-lg leading-relaxed line-clamp-2"
                >
                  {project.description}
                </motion.p>
              )}
            </motion.div>
          </div>
        </div>

        {/* ── Content container ── */}
        <div className="container-custom py-14">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">

            {/* ── Main column ── */}
            <div className="lg:col-span-2 space-y-8">

              {/* Image gallery */}
              {activeImage ? (
                <motion.div
                  variants={staggerContainer(0.1)}
                  initial="hidden"
                  animate="visible"
                  className="space-y-4"
                >
                  {/* Primary image with navigation */}
                  <motion.div
                    variants={scaleIn}
                    className="relative aspect-[16/9] bg-gradient-to-br from-[#004B4B] to-[#044a49] rounded-sm overflow-hidden shadow-sm group"
                  >
                    <img
                      src={activeImage}
                      alt={`${project.title} - صورة ${activeImageIndex + 1}`}
                      className="w-full h-full object-cover absolute inset-0 transition-opacity duration-300"
                    />

                    {/* Image index counter badge */}
                    {images.length > 1 && (
                      <div className="absolute top-3 end-3 bg-black/60 backdrop-blur-xs text-white text-xs font-semibold px-2.5 py-1 rounded-sm shadow-xs">
                        {activeImageIndex + 1} / {images.length}
                      </div>
                    )}

                    {/* Prev / Next buttons if multiple */}
                    {images.length > 1 && (
                      <>
                        <button
                          type="button"
                          onClick={() => setActiveImageIndex((prev) => (prev > 0 ? prev - 1 : images.length - 1))}
                          className="absolute start-3 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/80 text-white p-2 rounded-full opacity-80 group-hover:opacity-100 transition-opacity cursor-pointer shadow-md"
                          title="الصورة السابقة"
                        >
                          <svg className="w-5 h-5 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
                          </svg>
                        </button>
                        <button
                          type="button"
                          onClick={() => setActiveImageIndex((prev) => (prev < images.length - 1 ? prev + 1 : 0))}
                          className="absolute end-3 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/80 text-white p-2 rounded-full opacity-80 group-hover:opacity-100 transition-opacity cursor-pointer shadow-md"
                          title="الصورة التالية"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
                          </svg>
                        </button>
                      </>
                    )}
                  </motion.div>

                  {/* Thumbnails row (showing all images) */}
                  {images.length > 1 && (
                    <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6 gap-2.5 pt-1">
                      {images.map((img, i) => (
                        <button
                          key={i}
                          type="button"
                          onClick={() => setActiveImageIndex(i)}
                          className={`aspect-[4/3] rounded-sm overflow-hidden cursor-pointer relative transition-all duration-200 border-2 ${
                            i === activeImageIndex
                              ? "border-[var(--color-primary)] ring-2 ring-[var(--color-primary)]/40 scale-102 opacity-100 shadow-sm"
                              : "border-transparent opacity-70 hover:opacity-100"
                          }`}
                        >
                          <img
                            src={img}
                            alt={`${project.title} - صورة مصغرة ${i + 1}`}
                            className="w-full h-full object-cover absolute inset-0"
                          />
                        </button>
                      ))}
                    </div>
                  )}
                </motion.div>
              ) : (
                <div className="relative aspect-[16/9] bg-gradient-to-br from-teal-900/10 to-[#004B4B]/20 rounded-sm overflow-hidden flex flex-col items-center justify-center text-teal-900/50 border border-teal-900/15 p-8 text-center shadow-sm">
                  <svg className="w-16 h-16 text-[var(--color-primary)] opacity-40 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <p className="text-[var(--color-primary)] font-bold text-sm">صور المشروع قيد التحديث</p>
                </div>
              )}

              {/* Description */}
              <motion.div
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="bg-white rounded-sm p-8 shadow-sm border border-[#E2E8F0]"
              >
                <h2 className="text-xl font-black text-[var(--color-primary)] mb-4">نبذة عن المشروع</h2>
                <p className="text-[#646d70] leading-loose text-[0.97rem]">{project.description}</p>
              </motion.div>

              {/* Scope of work */}
              {project.scope && project.scope.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                  className="bg-white rounded-sm p-8 shadow-sm border border-[#E2E8F0]"
                >
                  <h2 className="text-xl font-black text-[var(--color-primary)] mb-6">نطاق العمل</h2>
                  <motion.ul
                    variants={staggerContainer(0.08, 0.3)}
                    initial="hidden"
                    animate="visible"
                    className="space-y-3"
                  >
                    {project.scope.map((item, i) => (
                      <motion.li
                        key={i}
                        variants={fadeInLeft}
                        className="flex items-start gap-3"
                      >
                        <motion.span
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: 0.3 + i * 0.07, type: "spring", stiffness: 200 }}
                          className="w-6 h-6 rounded-sm bg-[var(--color-primary)]/15 flex items-center justify-center flex-shrink-0 mt-0.5"
                        >
                          <svg className="w-3.5 h-3.5 text-[var(--color-primary)]" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </motion.span>
                        <span className="text-[#646d70] text-sm leading-relaxed">{item}</span>
                      </motion.li>
                    ))}
                  </motion.ul>
                </motion.div>
              )}
            </div>

            {/* ── Sidebar ── */}
            <div className="space-y-6">

              {/* Project specs card */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.15 }}
                className="bg-[var(--color-primary)] rounded-sm p-7 text-white"
              >
                <h3 className="font-black text-lg mb-6 text-[var(--color-secondary)]">تفاصيل المشروع</h3>
                <div className="space-y-4">
                  {[
                    { label: "الفئة",      value: project.category?.name },
                    { label: "الموقع",     value: project.location },
                    { label: "العميل",     value: project.client },
                    { label: "المساحة",    value: project.area },
                    { label: "الطوابق",    value: project.floors },
                    { label: "مدة التنفيذ",value: project.duration },
                    { label: "سنة التسليم",value: project.year },
                  ].filter(i => i.value && i.value !== "—").map((item) => (
                    <div key={item.label} className="flex justify-between items-start gap-2 pb-4 border-b border-white/8 last:border-0 last:pb-0">
                      <span className="text-white/50 text-sm">{item.label}</span>
                      <span className="text-white font-semibold text-sm text-end">{item.value}</span>
                    </div>
                  ))}
                </div>
              </motion.div>

              {/* File attachment */}
              {project.attachment_file && !project.attachment_file.startsWith("file:") && (
                <motion.div
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.25 }}
                  className="bg-white rounded-sm p-6 shadow-sm border border-[#E2E8F0]"
                >
                  <h3 className="font-black text-[var(--color-primary)] text-base mb-4">الملفات المرفقة</h3>
                  <motion.a
                    href={project.attachment_file}
                    download
                    whileHover={{ scale: 1.02, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex items-center gap-4 p-4 bg-[var(--color-secondary)] border border-[#E2E8F0] hover:border-[var(--color-primary)]/40 rounded-sm transition-all duration-200 group"
                  >
                    {/* PDF icon */}
                    <div className="w-11 h-11 rounded-sm bg-red-50 border border-red-100 flex items-center justify-center flex-shrink-0">
                      <svg className="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 1.5L18.5 9H13V3.5zM9.5 14.5c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5.67-1.5 1.5-1.5 1.5.67 1.5 1.5zm6 0c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5.67-1.5 1.5-1.5 1.5.67 1.5 1.5z"/>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-[var(--color-primary)] font-semibold text-sm truncate">{project.attachment_label || "ملف المشروع"}</p>
                      <p className="text-[#646d70] text-xs mt-0.5">اضغط للتحميل</p>
                    </div>
                    <motion.svg
                      className="w-5 h-5 text-[var(--color-primary)] flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      whileHover={{ y: 2 }}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </motion.svg>
                  </motion.a>
                </motion.div>
              )}

              {/* CTA card */}
              <motion.div
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.35 }}
                className="bg-[var(--color-primary)] rounded-sm p-7 text-white"
              >
                <h3 className="font-black text-lg mb-2">أريد مشروعاً مشابهاً</h3>
                <p className="text-white/80 text-sm mb-5 leading-relaxed">
                  تواصل معنا اليوم للحصول على عرض سعر مجاني لمشروعك
                </p>
                <motion.a
                  href="/#contact"
                  whileHover={{ scale: 1.03, y: -2 }}
                  whileTap={{ scale: 0.97 }}
                  className="block w-full bg-[var(--color-secondary)] text-[var(--color-primary)] text-center py-3 rounded-sm font-bold text-sm shadow-lg hover:bg-white"
                >
                  اطلب عرض سعر مجاني
                </motion.a>
              </motion.div>

            </div>
          </div>
        </div>
      </main>
  );
}
