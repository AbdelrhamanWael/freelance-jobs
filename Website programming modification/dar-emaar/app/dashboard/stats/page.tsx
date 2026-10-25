import { createServerClient } from "@/lib/supabase/server";
import Link from "next/link";
import DeleteStatButton from "@/components/dashboard/DeleteStatButton";

export const dynamic = "force-dynamic";

export default async function StatsDashboardPage() {
  const supabase = await createServerClient();
  const { data: stats, error } = await supabase
    .from("stats")
    .select("*")
    .order("sort_order", { ascending: true });

  if (error) {
    return <div className="text-red-500">حدث خطأ: {error.message}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1B2A4A]">أرقام الإنجازات</h1>
          <p className="text-sm text-[#64748B] mt-1">تحكم في الخانات التي تظهر في قسم الإحصائيات بالصفحة الرئيسية</p>
        </div>
        <Link
          href="/dashboard/stats/new"
          className="bg-[var(--color-primary)] text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-[var(--color-primary)]/90 transition-colors"
        >
          + إضافة خانة جديدة
        </Link>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-[#E2E8F0] overflow-hidden">
        <table className="w-full text-sm text-right">
          <thead className="bg-[#F8FAFC] text-[#64748B] border-b border-[#E2E8F0]">
            <tr>
              <th className="px-6 py-4 font-semibold">الترتيب</th>
              <th className="px-6 py-4 font-semibold">اسم الخانة</th>
              <th className="px-6 py-4 font-semibold">القيمة / الرقم</th>
              <th className="px-6 py-4 font-semibold">الحالة</th>
              <th className="px-6 py-4 font-semibold">الإجراءات</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E2E8F0]">
            {!stats || stats.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-[#64748B]">
                  لا توجد خانات مضافة حتى الآن.
                </td>
              </tr>
            ) : (
              stats.map((stat: any) => (
                <tr key={stat.id} className="hover:bg-[#F8FAFC]/50 transition-colors">
                  <td className="px-6 py-4 text-[#64748B]">{stat.sort_order}</td>
                  <td className="px-6 py-4 font-medium text-[#1B2A4A]">{stat.label}</td>
                  <td className="px-6 py-4 font-bold text-[var(--color-primary)]" dir="ltr">{stat.value}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${
                      stat.is_visible ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-500"
                    }`}>
                      {stat.is_visible ? "ظاهر" : "مخفي"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <Link
                        href={`/dashboard/stats/${stat.id}`}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        تعديل
                      </Link>
                      <DeleteStatButton id={stat.id} label={stat.label} />
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="bg-[var(--color-secondary)]/50 border border-[var(--color-primary)]/10 rounded-xl p-4 text-sm text-[#64748B]">
        💡 <strong>تلميح:</strong> الخانات تظهر في الصفحة الرئيسية بنفس ترتيب الأرقام. يمكنك إخفاء خانة بدون حذفها عن طريق الضغط على "تعديل" وإلغاء تحديد "ظاهر في الموقع".
      </div>
    </div>
  );
}
