import { Suspense } from "react";
import { getDbCategories, getDbProjects } from "@/lib/db-projects";
import ProjectsGrid from "@/components/projects/ProjectsGrid";
import CategoryFilter from "@/components/projects/CategoryFilter";
import type { Metadata } from "next";
import Navbar from "@/components/landing/Navbar";
import Footer from "@/components/landing/Footer";
import { getSettings } from "@/lib/settings";
import { getPageContent } from "@/lib/content";

export const metadata: Metadata = {
  title: "مشاريعنا | دار اعمار الغربية",
  description: "تصفح أبرز مشاريع دار اعمار الغربية في التصميم والبناء والتشطيبات وإدارة المشاريع.",
};

type Props = {
  searchParams: Promise<{ category?: string }>;
};

export default async function ProjectsPage({ searchParams }: Props) {
  const { category } = await searchParams;
  const activeCategory = category || "all";

  const [categories, allProjects] = await Promise.all([
    getDbCategories(),
    getDbProjects(),
  ]);

  // Filter projects client-side from the full list (avoids extra DB call)
  const filteredProjects =
    activeCategory === "all"
      ? allProjects
      : allProjects.filter((p) => p.category?.slug === activeCategory);

  const settings = await getSettings();
  const content = await getPageContent();

  return (
    <>
      <Navbar 
        isBlogEnabled={settings.is_blog_enabled} 
        headerCtaText={content.header_cta_text}
        logoUrl={settings.logo_url}
      />
      <main className="min-h-screen" style={{ background: "var(--color-secondary, #F9F3EC)" }}>

      {/* Page Header */}
      <section
        className="py-20 pt-32 text-center relative overflow-hidden"
        style={{ background: "var(--color-primary, #004B4B)" }}
      >
        {/* Subtle grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.04] pointer-events-none"
          style={{
            backgroundImage: `repeating-linear-gradient(45deg, #fff 0, #fff 1px, transparent 0, transparent 50px)`,
          }}
        />
        <div className="relative z-10 container mx-auto px-6">
          <div className="flex justify-center mb-6">
            <a
              href="/"
              className="inline-flex items-center gap-2 text-white/70 hover:text-white text-sm transition-colors group"
            >
              <svg className="w-4 h-4 rotate-180 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              العودة للرئيسية
            </a>
          </div>
          <span
            className="inline-block text-sm font-bold tracking-widest uppercase mb-4 px-4 py-1.5 rounded-full"
            style={{ background: "rgba(255,255,255,0.15)", color: "#2dd4bf" }}
          >
            {content.projects_page_badge || "معرض الأعمال"}
          </span>
          <h1 className="text-4xl sm:text-5xl font-black text-white mb-4">
            {content.projects_page_title || "مشاريعنا"}
          </h1>
          <p className="text-white/80 text-lg max-w-xl mx-auto">
            {content.projects_page_subtitle || "أكثر من 200 مشروع منجز عبر مختلف القطاعات — تصفح أبرز إنجازاتنا"}
          </p>
        </div>
      </section>

      {/* Filter + Grid */}
      <div className="container mx-auto px-6 py-14">

        {/* Category Filter Bar */}
        <Suspense fallback={null}>
          <CategoryFilter
            categories={categories}
            activeCategory={activeCategory}
            totalCount={allProjects.length}
          />
        </Suspense>

        {/* Projects Grid */}
        <div className="mt-8">
          {filteredProjects.length === 0 ? (
            <div className="text-center py-24">
              <p className="text-5xl mb-4">🏗️</p>
              <p className="text-[#6C6D71] font-semibold text-lg">لا توجد مشاريع في هذه الفئة حتى الآن</p>
              <a
                href="/projects"
                className="inline-block mt-4 text-sm font-semibold underline"
                style={{ color: "var(--color-primary, #004B4B)" }}
              >
                عرض جميع المشاريع
              </a>
            </div>
          ) : (
            <ProjectsGrid projects={filteredProjects} />
          )}
        </div>

        {/* CTA */}
        <div
          className="mt-16 text-center py-12 rounded-2xl"
          style={{ background: "var(--color-primary, #004B4B)" }}
        >
          <h2 className="text-2xl sm:text-3xl font-black text-white mb-3">
            {content.projects_page_cta_title || "هل لديك مشروع مماثل؟"}
          </h2>
          <p className="text-white/80 mb-6 text-base">
            {content.projects_page_cta_desc || "احصل على استشارة مجانية من فريق خبرائنا"}
          </p>
          <a
            href="/#contact"
            className="inline-block px-8 py-3.5 rounded-lg font-bold text-sm sm:text-base transition-all hover:opacity-90 shadow-md"
            style={{
              background: "var(--color-secondary, #F9F3EC)",
              color: "var(--color-primary, #004B4B)",
            }}
          >
            {content.projects_page_cta_button || "طلب استشارة مجانية"}
          </a>
        </div>
      </div>
    </main>
    <Footer />
  </>
  );
}
