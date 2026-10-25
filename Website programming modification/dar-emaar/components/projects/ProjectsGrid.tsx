"use client";

import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import type { DbProject } from "@/lib/db-projects";
import { Star, Building2 } from "lucide-react";

type Props = {
  projects: DbProject[];
};

export default function ProjectsGrid({ projects }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project, i) => {
        const thumbnail = project.images?.[project.thumbnail_index ?? 0] ?? null;

        return (
          <motion.div
            key={project.id}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: i * 0.07, ease: [0.22, 1, 0.36, 1] }}
          >
            <Link
              href={`/projects/${project.slug}`}
              className="group block bg-white rounded-xl overflow-hidden shadow-sm border border-[#E2E8F0] hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
            >
              {/* Thumbnail */}
              <div className="relative h-48 overflow-hidden bg-[#F1F5F9]">
                {thumbnail ? (
                  <Image
                    src={thumbnail}
                    alt={project.title}
                    fill
                    unoptimized
                    className="object-cover group-hover:scale-105 transition-transform duration-500"
                    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                  />
                ) : (
                  <div
                    className="w-full h-full flex items-center justify-center text-4xl"
                    style={{ background: "var(--color-primary, #004B4B)", opacity: 0.08 }}
                  >
                    <Building2 className="w-12 h-12 text-[var(--color-primary)] opacity-40" />
                  </div>
                )}

                {/* Multiple Images Counter Badge */}
                {project.images && project.images.length > 1 && (
                  <div className="absolute bottom-2.5 end-2.5 bg-black/70 backdrop-blur-xs text-white text-[11px] font-bold px-2 py-0.5 rounded-md flex items-center gap-1 shadow-sm">
                    <svg className="w-3.5 h-3.5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span>{project.images.length} صور</span>
                  </div>
                )}

                {/* Category badge */}
                {project.category && (
                  <div className="absolute top-3 start-3">
                    <span
                      className="text-xs font-bold px-2.5 py-1 rounded-sm"
                      style={{
                        background: "var(--color-primary, #004B4B)",
                        color: "var(--color-secondary, #F9F3EC)",
                      }}
                    >
                      {project.category.name}
                    </span>
                  </div>
                )}

                {/* Featured badge */}
                {project.is_featured && (
                  <div className="absolute top-3 end-3">
                    <span className="text-xs font-bold px-2 py-1 rounded-sm bg-amber-400 text-amber-900 flex items-center gap-1">
                      <Star className="w-3.5 h-3.5 fill-amber-700 text-amber-700" />
                      مميز
                    </span>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="p-5">
                <h3
                  className="text-lg font-bold mb-2 line-clamp-2 group-hover:underline"
                  style={{ color: "var(--color-primary, #004B4B)" }}
                >
                  {project.title}
                </h3>

                <div className="flex flex-wrap gap-3 text-xs mb-3" style={{ color: "var(--color-accent, #6C6D71)" }}>
                  {project.location && (
                    <span className="flex items-center gap-1">
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {project.location}
                    </span>
                  )}
                  {project.year && (
                    <span className="flex items-center gap-1">
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {project.year}
                    </span>
                  )}
                  {project.area && (
                    <span>{project.area}</span>
                  )}
                </div>

                <p className="text-sm line-clamp-2" style={{ color: "var(--color-accent, #6C6D71)" }}>
                  {project.description}
                </p>

                <div
                  className="mt-4 text-sm font-semibold flex items-center gap-1 group-hover:gap-2 transition-all"
                  style={{ color: "var(--color-primary, #004B4B)" }}
                >
                  عرض تفاصيل المشروع
                  <svg className="w-4 h-4 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </Link>
          </motion.div>
        );
      })}
    </div>
  );
}
