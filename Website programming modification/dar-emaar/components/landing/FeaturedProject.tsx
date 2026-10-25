"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import Link from "next/link";
import type { DbProject } from "@/lib/db-projects";
import type { PageContent } from "@/lib/content";
import { staggerContainer, scaleIn } from "@/lib/animations";

export default function FeaturedProject({ 
  projects, 
  content 
}: { 
  projects: DbProject[]; 
  content?: PageContent;
}) {
  // First project is the "featured" hero card; rest fill the grid
  const featuredProject = projects[0];
  const gridProjects = projects.slice(1, 7); // Show max 6 in grid
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });
  const titleRef = useRef<HTMLDivElement>(null);
  const titleInView = useInView(titleRef, { once: true, margin: "-60px" });
  const gridRef = useRef<HTMLDivElement>(null);
  const gridInView = useInView(gridRef, { once: true, margin: "-60px" });

  return (
    <section id="projects" className="section-padding bg-[#0e2530] relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-[#004B4B]/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-[#2dd4bf]/10 rounded-full blur-3xl pointer-events-none" />

      <div className="container-custom relative z-10">

        {/* Header */}
        <motion.div
          ref={titleRef}
          initial={{ opacity: 0, y: 30 }}
          animate={titleInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
          className="text-center mb-14"
        >
          {/* Prominent, Luminous High-Contrast Badge */}
          <div className="inline-flex items-center gap-2.5 px-5 py-2 rounded-full bg-[#004B4B]/40 border border-[#2dd4bf]/50 text-[#2dd4bf] text-sm sm:text-base font-extrabold tracking-wide mb-4 shadow-[0_0_20px_rgba(45,212,191,0.2)] backdrop-blur-md">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#2dd4bf] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#2dd4bf]"></span>
            </span>
            <span>{content?.projects_badge || "مشاريعنا"}</span>
          </div>

          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white section-title leading-tight">
            {content?.projects_title || "مشاريع نفخر بتنفيذها"}
          </h2>
          <p className="text-white/80 mt-5 max-w-2xl mx-auto leading-relaxed text-base sm:text-lg font-normal">
            {content?.projects_subtitle || "نفخر بتسليم مشاريع تتجاوز توقعات عملائنا في الجودة والالتزام بالمواعيد"}
          </p>
        </motion.div>

        {/* Featured project — split slide-in from sides */}
        <div ref={ref} className="bg-white/5 border border-white/10 rounded-xl overflow-hidden mb-10 shadow-2xl backdrop-blur-sm">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-0">

            {/* Image — slides in from right */}
            <motion.div
              initial={{ opacity: 0, x: 60 }}
              animate={isInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.75, ease: [0.22, 1, 0.36, 1] }}
              className="relative h-72 lg:h-auto bg-gradient-to-br from-[#163645] to-[#0e2530] flex items-center justify-center overflow-hidden"
            >
              <div className="text-center text-white/30">
                {featuredProject?.images?.[0] ? (
                  <img src={featuredProject.images[0]} alt={featuredProject.title} className="w-full h-full object-cover absolute inset-0 opacity-50 mix-blend-overlay hover:scale-105 transition-transform duration-700" />
                ) : (
                  <svg className="w-16 h-16 mx-auto mb-3 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                )}
              </div>
              <div className="absolute top-4 start-4 bg-[var(--color-primary,#004B4B)] border border-white/20 text-white text-xs sm:text-sm font-bold px-4 py-1.5 rounded-lg z-10 shadow-lg backdrop-blur-sm">
                {content?.projects_featured_label || "مشروع مميز"}
              </div>
            </motion.div>

            {/* Details — slides in from left */}
            <motion.div
              initial={{ opacity: 0, x: -60 }}
              animate={isInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.75, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
              className="p-8 lg:p-12 flex flex-col justify-center"
            >
              <span className="text-[#2dd4bf] font-bold text-sm sm:text-base mb-2">
                {featuredProject?.category?.name || ""} {featuredProject?.location ? `— ${featuredProject.location}` : ""}
              </span>
              <h3 className="text-2xl sm:text-3xl font-black text-white mb-4 leading-snug">
                {featuredProject?.title || "لا توجد مشاريع مميزة"}
              </h3>
              <p className="text-white/70 leading-relaxed mb-6 text-sm sm:text-base">
                {featuredProject?.description || "قم بإضافة مشاريع مميزة من لوحة التحكم لتظهر هنا."}
              </p>

              <motion.div
                variants={staggerContainer(0.1, 0.3)}
                initial="hidden"
                animate={isInView ? "visible" : "hidden"}
                className="grid grid-cols-3 gap-4 mb-8"
              >
                {[
                  { label: "المساحة", value: featuredProject?.area || "—" },
                  { label: "المدة", value: featuredProject?.duration || "—" },
                  { label: "السنة", value: featuredProject?.year || "—" },
                ].map((item) => (
                  <motion.div key={item.label} variants={scaleIn} className="text-center bg-white/5 border border-white/10 rounded-lg p-3">
                    <p className="text-white font-bold text-base sm:text-lg">{item.value}</p>
                    <p className="text-white/60 text-xs mt-0.5">{item.label}</p>
                  </motion.div>
                ))}
              </motion.div>

              <motion.a
                href="#contact"
                whileHover={{ scale: 1.03, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className="inline-flex items-center justify-center gap-2 bg-[var(--color-primary,#004B4B)] hover:bg-[#005f5f] transition-all text-white px-7 py-3.5 rounded-lg font-bold text-sm sm:text-base shadow-[0_4px_20px_rgba(0,75,75,0.4)] w-fit"
              >
                {content?.projects_featured_cta || "أريد مشروعاً مشابهاً"}
                <svg className="w-4 h-4 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
                </svg>
              </motion.a>
            </motion.div>
          </div>
        </div>

        {/* Image grid — staggered reveal, each links to detail page */}
        <motion.div
          ref={gridRef}
          variants={staggerContainer(0.08)}
          initial="hidden"
          animate={gridInView ? "visible" : "hidden"}
          className="grid grid-cols-2 md:grid-cols-3 gap-4"
        >
          {gridProjects.map((project) => (
            <Link key={project.slug} href={`/projects/${project.slug}`}>
              <motion.div
                variants={scaleIn}
                whileHover={{ scale: 1.03, zIndex: 1 }}
                transition={{ duration: 0.25 }}
                className="relative aspect-[4/3] bg-gradient-to-br from-[#163645] to-[#0e2530] rounded-lg overflow-hidden cursor-pointer border border-white/10 group"
              >
                {/* Category badge */}
                <div className="absolute top-2.5 start-2.5 z-10">
                  <span className="text-xs font-bold text-white bg-[#0e2530]/85 border border-[#2dd4bf]/40 px-2.5 py-1 rounded-md backdrop-blur-sm">
                    {project.category?.name}
                  </span>
                </div>
                {/* Placeholder image icon */}
                <div className="absolute inset-0 flex items-center justify-center text-white/20">
                  {project.images?.[0] ? (
                    <img src={project.images[0]} alt={project.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                  ) : (
                    <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  )}
                </div>
                {/* Hover overlay with title */}
                <motion.div
                  initial={{ opacity: 0 }}
                  whileHover={{ opacity: 1 }}
                  className="absolute inset-0 bg-[#0e2530]/80 backdrop-blur-xs flex flex-col items-center justify-center gap-1.5 p-4 transition-opacity"
                >
                  <span className="text-white font-bold text-sm sm:text-base text-center leading-tight">{project.title}</span>
                  <span className="text-[#2dd4bf] text-xs font-semibold flex items-center gap-1 mt-1">
                    عرض التفاصيل
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" />
                    </svg>
                  </span>
                </motion.div>
              </motion.div>
            </Link>
          ))}
        </motion.div>

        {/* View all projects CTA */}
        <div className="mt-16 text-center">
          <Link
            href="/projects"
            className="inline-flex items-center justify-center gap-2 bg-white/5 border border-white/20 hover:bg-white/15 hover:border-white/40 transition-all text-white px-9 py-3.5 rounded-lg font-bold text-sm sm:text-base shadow-sm backdrop-blur-sm"
          >
            {content?.projects_view_all_cta || "عرض جميع المشاريع"}
            <svg className="w-4 h-4 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>

      </div>
    </section>
  );
}

