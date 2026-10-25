import { createServerClient } from "@/lib/supabase/server";
import Link from "next/link";
import { revalidatePath } from "next/cache";

export const dynamic = "force-dynamic";

export default async function BlogDashboardPage() {
  const supabase = await createServerClient();
  const { data: posts, error } = await supabase
    .from("blog_posts")
    .select("id, title, slug, is_published, created_at")
    .order("created_at", { ascending: false });

  if (error) {
    return <div className="text-red-500">حدث خطأ أثناء جلب المقالات: {error.message}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1B2A4A]">المدونة</h1>
        <Link
          href="/dashboard/blog/new"
          className="bg-[#004B4B] text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-[#004B4B]/90 transition-colors"
        >
          + كتابة مقال جديد
        </Link>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-[#E2E8F0] overflow-hidden">
        <table className="w-full text-sm text-right">
          <thead className="bg-[#F8FAFC] text-[#64748B] border-b border-[#E2E8F0]">
            <tr>
              <th className="px-6 py-4 font-semibold">عنوان المقال</th>
              <th className="px-6 py-4 font-semibold">تاريخ الإنشاء</th>
              <th className="px-6 py-4 font-semibold">الحالة</th>
              <th className="px-6 py-4 font-semibold">الإجراءات</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E2E8F0]">
            {posts?.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-[#64748B]">
                  لا توجد مقالات مضافة حتى الآن.
                </td>
              </tr>
            ) : (
              posts?.map((post: any) => (
                <tr key={post.id} className="hover:bg-[#F8FAFC]/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-[#1B2A4A]">{post.title}</td>
                  <td className="px-6 py-4 text-[#64748B]">
                    {new Date(post.created_at).toLocaleDateString("ar-SA")}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${
                        post.is_published
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-amber-100 text-amber-700"
                      }`}
                    >
                      {post.is_published ? "منشور" : "مسودة"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <Link
                        href={`/dashboard/blog/${post.slug}`}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        تعديل
                      </Link>
                      <form action={async () => {
                        "use server";
                        const client = await createServerClient();
                        await client.from("blog_posts").delete().eq("id", post.id);
                        revalidatePath("/", "layout");
                      }}>
                        <button type="submit" className="text-red-500 hover:text-red-700 font-medium">
                          حذف
                        </button>
                      </form>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
