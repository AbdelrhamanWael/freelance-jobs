import { redirect } from "next/navigation";
import { getSettings } from "@/lib/settings";
import { createServerClient } from "@/lib/supabase/server";
import Link from "next/link";
import { FileText } from "lucide-react";
import type { Metadata } from "next";
import Navbar from "@/components/landing/Navbar";
import Footer from "@/components/landing/Footer";
import { getPageContent } from "@/lib/content";

export const metadata: Metadata = {
  title: "المدونة | دار اعمار الغربية",
  description: "مقالات ونصائح في عالم المقاولات والبناء والتصميم.",
};

export default async function BlogPage() {
  // If blog is disabled, redirect to home
  const settings = await getSettings();
  if (!settings.is_blog_enabled) {
    redirect("/");
  }

  const supabase = await createServerClient();
  const { data: posts = [] } = await supabase
    .from("blog_posts")
    .select("slug, title, excerpt, cover_image, author, created_at, tags")
    .eq("is_published", true)
    .order("created_at", { ascending: false });

  const content = await getPageContent();

  return (
    <>
      <Navbar 
        isBlogEnabled={settings.is_blog_enabled} 
        headerCtaText={content.header_cta_text}
        logoUrl={settings.logo_url}
      />
      <main className="min-h-screen" style={{ background: "var(--color-secondary, #F9F3EC)" }}>
      {/* Header */}
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
            className="inline-block text-sm font-bold tracking-widest uppercase mb-4 px-4 py-1.5 rounded-sm"
            style={{ background: "rgba(255,255,255,0.1)", color: "rgba(255,255,255,0.8)" }}
          >
            الأخبار والمقالات
          </span>
          <h1 className="text-4xl sm:text-5xl font-black text-white mb-3">المدونة</h1>
          <p className="text-white/70 text-lg max-w-xl mx-auto">نصائح وأفكار من خبراء دار اعمار الغربية</p>
        </div>
      </section>

      <div className="container mx-auto px-6 py-14">
        {posts && posts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {posts.map((blog) => (
              <Link 
                href={`/blog/${blog.slug}`} 
                key={blog.slug}
                className="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col border border-[var(--color-accent)]/10"
              >
                <div className="relative h-56 w-full overflow-hidden bg-gray-100">
                  {blog.cover_image &&
                  !blog.cover_image.startsWith("file:") &&
                  (blog.cover_image.startsWith("http://") ||
                    blog.cover_image.startsWith("https://") ||
                    blog.cover_image.startsWith("/")) ? (
                    <img
                      src={blog.cover_image}
                      alt={blog.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#004B4B]/15 to-[#004B4B]/5 text-[var(--color-primary)]">
                      <svg className="w-12 h-12 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                      </svg>
                    </div>
                  )}
                </div>
                <div className="p-6 flex flex-col flex-1">
                  <p className="text-xs font-bold text-[var(--color-accent)] mb-2">
                    {new Date(blog.created_at).toLocaleDateString("ar-SA", { year: 'numeric', month: 'long', day: 'numeric' })}
                  </p>
                  <h3 className="text-xl font-bold text-[var(--color-primary)] mb-3 line-clamp-2">
                    {blog.title}
                  </h3>
                  <p className="text-[var(--color-accent)] text-sm mb-4 line-clamp-3">
                    {blog.excerpt}
                  </p>
                  <div className="mt-auto flex items-center text-[var(--color-primary)] font-bold text-sm gap-2 group-hover:gap-3 transition-all">
                    <span>اقرأ المزيد</span>
                    <svg className="w-4 h-4 rtl:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-24">
            <FileText className="w-12 h-12 text-[var(--color-accent)]/30 mx-auto mb-4" />
            <p className="font-semibold text-lg" style={{ color: "var(--color-accent, #6C6D71)" }}>
              لا توجد مقالات بعد. ترقبونا!
            </p>
          </div>
        )}
      </div>
    </main>
    <Footer />
  </>
  );
}
