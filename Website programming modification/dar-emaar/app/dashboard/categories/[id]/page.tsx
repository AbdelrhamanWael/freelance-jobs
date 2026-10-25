import { createServerClient } from "@/lib/supabase/server";
import { notFound } from "next/navigation";
import CategoryForm from "@/components/dashboard/CategoryForm";

export const dynamic = "force-dynamic";

export default async function EditCategoryPage(props: { params: Promise<{ id: string }> }) {
  const params = await props.params;
  const { id } = params;
  const isNew = id === "new";

  const supabase = await createServerClient();

  let category = null;
  if (!isNew) {
    const { data } = await supabase.from("categories").select("*").eq("id", id).single();
    if (!data) notFound();
    category = data;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-[#1B2A4A]">
        {isNew ? "إضافة فئة جديدة" : "تعديل الفئة"}
      </h1>
      
      <div className="bg-white p-6 rounded-xl shadow-sm border border-[#E2E8F0]">
        <CategoryForm category={category} />
      </div>
    </div>
  );
}
