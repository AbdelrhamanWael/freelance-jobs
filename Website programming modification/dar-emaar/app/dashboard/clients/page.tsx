import { createServerClient } from "@/lib/supabase/server";
import Link from "next/link";
import { revalidatePath } from "next/cache";

export const dynamic = "force-dynamic";

export default async function ClientsDashboardPage() {
  const supabase = await createServerClient();
  const { data: clients, error } = await supabase
    .from("clients")
    .select("id, name, logo_url, is_published, sort_order")
    .order("sort_order", { ascending: true })
    .order("created_at", { ascending: true });

  if (error) {
    return <div className="text-red-500">حدث خطأ أثناء جلب العملاء: {error.message}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1B2A4A]">شركاء النجاح (العملاء)</h1>
        <Link
          href="/dashboard/clients/new"
          className="bg-[#004B4B] text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-[#004B4B]/90 transition-colors"
        >
          + إضافة عميل جديد
        </Link>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-[#E2E8F0] overflow-hidden">
        <table className="w-full text-sm text-right">
          <thead className="bg-[#F8FAFC] text-[#64748B] border-b border-[#E2E8F0]">
            <tr>
              <th className="px-6 py-4 font-semibold">الشعار</th>
              <th className="px-6 py-4 font-semibold">الاسم</th>
              <th className="px-6 py-4 font-semibold">الترتيب</th>
              <th className="px-6 py-4 font-semibold">الحالة</th>
              <th className="px-6 py-4 font-semibold">الإجراءات</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E2E8F0]">
            {clients?.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-[#64748B]">
                  لا يوجد عملاء مضافين حتى الآن.
                </td>
              </tr>
            ) : (
              clients?.map((client: any) => (
                <tr key={client.id} className="hover:bg-[#F8FAFC]/50 transition-colors">
                  <td className="px-6 py-4">
                    {client.logo_url ? (
                      <img src={client.logo_url} alt={client.name} className="h-10 w-auto object-contain" />
                    ) : (
                      <span className="text-xs bg-gray-100 text-gray-500 px-2 py-1 rounded">نص فقط</span>
                    )}
                  </td>
                  <td className="px-6 py-4 font-medium text-[#1B2A4A]">{client.name}</td>
                  <td className="px-6 py-4 text-[#64748B]">{client.sort_order}</td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${
                        client.is_published
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-amber-100 text-amber-700"
                      }`}
                    >
                      {client.is_published ? "ظاهر" : "مخفي"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <Link
                        href={`/dashboard/clients/${client.id}`}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        تعديل
                      </Link>
                      <form action={async () => {
                        "use server";
                        const supa = await createServerClient();
                        await supa.from("clients").delete().eq("id", client.id);
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
