import { createServerClient } from "@/lib/supabase/server";
import DashboardStats from "@/components/dashboard/DashboardStats";

export const metadata = {
  title: "لوحة التحكم — دار اعمار الغربية",
};

export default async function DashboardPage() {
  const supabase = await createServerClient();

  // Fetch all leads for stats computation
  const { data: leads = [] } = await supabase
    .from("leads")
    .select("id, status, source, service, created_at")
    .order("created_at", { ascending: false });

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-black text-[#1B2A4A]">نظرة عامة</h1>
        <p className="text-[#64748B] text-sm mt-1">
          {new Date().toLocaleDateString("ar-SA", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
        </p>
      </div>
      <DashboardStats leads={leads || []} />
    </div>
  );
}
