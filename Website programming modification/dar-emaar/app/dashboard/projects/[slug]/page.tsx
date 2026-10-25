import { createServerClient } from "@/lib/supabase/server";
import { notFound } from "next/navigation";
import ProjectForm from "@/components/dashboard/ProjectForm";

export const dynamic = "force-dynamic";

export default async function EditProjectPage(props: { params: Promise<{ slug: string }> }) {
  const params = await props.params;
  const { slug } = params;
  const isNew = slug === "new";

  const supabase = await createServerClient();

  // Fetch categories for the select dropdown
  const { data: categories } = await supabase.from("categories").select("*").order("sort_order");

  let project = null;
  if (!isNew) {
    let decodedSlug = slug;
    try {
      decodedSlug = decodeURIComponent(slug);
    } catch {
      decodedSlug = slug;
    }

    let { data } = await supabase.from("projects").select("*").eq("slug", decodedSlug).maybeSingle();
    if (!data && decodedSlug !== slug) {
      const res = await supabase.from("projects").select("*").eq("slug", slug).maybeSingle();
      data = res.data;
    }
    if (!data) {
      const resById = await supabase.from("projects").select("*").eq("id", slug).maybeSingle();
      data = resById.data;
    }
    if (!data) notFound();
    project = data;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-[#1B2A4A]">
        {isNew ? "إضافة مشروع جديد" : "تعديل المشروع"}
      </h1>
      
      <div className="bg-white p-6 rounded-xl shadow-sm border border-[#E2E8F0]">
        <ProjectForm project={project} categories={categories || []} />
      </div>
    </div>
  );
}
