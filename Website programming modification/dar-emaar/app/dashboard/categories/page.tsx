import { createServerClient } from "@/lib/supabase/server";
import Link from "next/link";
import DeleteCategoryButton from "@/components/dashboard/DeleteCategoryButton";
import { Info, ArrowLeft } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function CategoriesDashboardPage() {
  const supabase = await createServerClient();
  const { data: categories, error } = await supabase
    .from("categories")
    .select("*")
    .order("sort_order", { ascending: true });

  if (error) {
    return <div className="text-red-500">حدث خطأ أثناء جلب الفئات: {error.message}</div>;
  }

  return (
    <div className="space-y-6">
      {/* Informational Guidance Banner */}
      <div className="bg-gradient-to-r from-teal-50 to-emerald-50 border border-teal-200/80 rounded-2xl p-4 sm:p-5 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="w-9 h-9 rounded-xl bg-[var(--color-primary)] text-white flex items-center justify-center flex-shrink-0 shadow-sm mt-0.5 sm:mt-0">
            <Info className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-[#1B2A4A] flex items-center gap-2">
              تنويه: هل تبحث عن تعديل خيارات «الخدمة المطلوبة» في صفحة تواصل معنا؟
            </h2>
            <p className="text-xs text-[#475569] mt-1 leading-relaxed">
              هذه الصفحة مخصصة لـ <strong>تصنيفات معرض المشاريع</strong> (مثل: سكني، تجاري، إلخ).
              إذا كنت ترغب في تعديل أو إضافة أو حذف فئات <strong>«الخدمة المطلوبة»</strong> المنسدلة في نموذج تواصل معنا (من 1 إلى 6 خانات كحد أقصى)، يمكنك إدارتها مباشرة من صفحة الإعدادات.
            </p>
          </div>
        </div>
        <Link
          href="/dashboard/settings?tab=contact_services"
          className="inline-flex items-center justify-center gap-2 bg-[var(--color-primary)] hover:bg-[var(--color-primary)]/90 text-white text-xs font-bold px-4 py-2.5 rounded-xl transition-all shadow-sm flex-shrink-0 text-center"
        >
          <span>إدارة فئات تواصل معنا (1 - 6)</span>
          <ArrowLeft className="w-3.5 h-3.5" />
        </Link>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1B2A4A]">تصنيفات المشاريع</h1>
          <p className="text-xs text-[#64748B] mt-0.5">الفئات المعمارية المستخدمة لتصنيف المشاريع في المعرض</p>
        </div>
        <Link
          href="/dashboard/categories/new"
          className="bg-[var(--color-primary)] text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-[var(--color-primary)]/90 transition-colors"
        >
          + إضافة فئة جديدة
        </Link>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-[#E2E8F0] overflow-hidden">
        <table className="w-full text-sm text-right">
          <thead className="bg-[#F8FAFC] text-[#64748B] border-b border-[#E2E8F0]">
            <tr>
              <th className="px-6 py-4 font-semibold">الترتيب</th>
              <th className="px-6 py-4 font-semibold">اسم الفئة</th>
              <th className="px-6 py-4 font-semibold">الرابط المختصر (Slug)</th>
              <th className="px-6 py-4 font-semibold">الإجراءات</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E2E8F0]">
            {categories?.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-[#64748B]">
                  لا توجد فئات مضافة حتى الآن.
                </td>
              </tr>
            ) : (
              categories?.map((category: any) => (
                <tr key={category.id} className="hover:bg-[#F8FAFC]/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-[#1B2A4A]">{category.sort_order}</td>
                  <td className="px-6 py-4 font-medium text-[var(--color-primary)]">{category.name}</td>
                  <td className="px-6 py-4 text-[#64748B]" dir="ltr">{category.slug}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <Link
                        href={`/dashboard/categories/${category.id}`}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        تعديل
                      </Link>
                      <DeleteCategoryButton id={category.id} name={category.name} />
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
