import { getRecentBlogs } from "@/lib/db-blogs";
import Link from "next/link";
import Image from "next/image";

export default async function RecentBlogs() {
  const blogs = await getRecentBlogs(3);


  return (
    <section id="blog" className="py-24 bg-[var(--color-secondary)]">
      <div className="container-custom">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-primary)] mb-4">
            أحدث المقالات والأخبار
          </h2>
          <p className="text-[var(--color-accent)]">
            تابع أحدث الأخبار والنصائح في عالم البناء والمقاولات من خبرائنا.
          </p>
        </div>

        {blogs.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl border border-[var(--color-accent)]/10">
            <p className="text-[#6C6D71] font-semibold text-lg">لا توجد مقالات مضافة حالياً.</p>
            <p className="text-sm mt-2 text-[#6C6D71]/70">سيتم عرض المقالات هنا فور نشرها من لوحة التحكم.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {blogs.map((blog) => (
              <Link 
                href={`/blog/${blog.slug}`} 
                key={blog.id}
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
        )}

        {/* View all blogs CTA */}
        <div className="mt-16 text-center">
          <Link
            href="/blog"
            className="inline-flex items-center justify-center gap-2 bg-transparent border border-[var(--color-primary)]/20 hover:bg-[var(--color-primary)]/5 transition-colors text-[var(--color-primary)] px-8 py-3 rounded-sm font-bold text-sm"
          >
            عرض جميع المدونات
            <svg className="w-4 h-4 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      </div>
    </section>
  );
}
