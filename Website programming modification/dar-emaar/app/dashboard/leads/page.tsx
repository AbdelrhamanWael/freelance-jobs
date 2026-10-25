import { createServerClient } from "@/lib/supabase/server";
import LeadsTable from "@/components/dashboard/LeadsTable";

export const metadata = {
  title: "العملاء المحتملون — لوحة التحكم",
};

export default async function LeadsPage() {
  const supabase = await createServerClient();

  const { data: leads = [] } = await supabase
    .from("leads")
    .select("*")
    .order("created_at", { ascending: false });

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-[#1B2A4A]">العملاء المحتملون</h1>
          <p className="text-[#64748B] text-sm mt-1">
            إجمالي {leads?.length || 0} طلب مسجّل
          </p>
        </div>
      </div>
      <LeadsTable initialLeads={leads || []} />
    </div>
  );
}
