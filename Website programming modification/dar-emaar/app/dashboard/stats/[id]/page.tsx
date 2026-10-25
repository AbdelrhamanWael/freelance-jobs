import { createServerClient } from "@/lib/supabase/server";
import { notFound } from "next/navigation";
import StatForm from "@/components/dashboard/StatForm";

export const dynamic = "force-dynamic";

export default async function EditStatPage(props: { params: Promise<{ id: string }> }) {
  const params = await props.params;
  const { id } = params;
  const isNew = id === "new";

  let stat = null;
  if (!isNew) {
    const supabase = await createServerClient();
    const { data } = await supabase.from("stats").select("*").eq("id", id).single();
    if (!data) notFound();
    stat = data;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-[#1B2A4A]">
        {isNew ? "إضافة خانة جديدة" : "تعديل الخانة"}
      </h1>
      <div className="bg-white p-6 rounded-xl shadow-sm border border-[#E2E8F0]">
        <StatForm stat={stat} />
      </div>
    </div>
  );
}
