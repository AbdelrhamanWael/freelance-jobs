import { createServerClient } from "@/lib/supabase/server";
import ClientForm from "@/components/dashboard/ClientForm";
import { notFound } from "next/navigation";

export default async function EditClientPage({ params }: { params: { id: string } }) {
  const supabase = await createServerClient();
  const { data: client, error } = await supabase
    .from("clients")
    .select("*")
    .eq("id", params.id)
    .single();

  if (error || !client) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B2A4A]">تعديل بيانات العميل</h1>
      <ClientForm client={client} />
    </div>
  );
}
