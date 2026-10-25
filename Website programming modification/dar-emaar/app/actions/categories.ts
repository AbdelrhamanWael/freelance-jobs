"use server";

import { revalidatePath } from "next/cache";
import { createServerClient, checkAuth } from "@/lib/supabase/server";

export async function saveCategory(formData: FormData) {
  await checkAuth();
  const supabase = await createServerClient();

  const id = formData.get("id") as string | null;
  const name = formData.get("name") as string;
  const slug = formData.get("slug") as string;
  const sort_order_raw = formData.get("sort_order") as string;
  const sort_order = parseInt(sort_order_raw, 10) || 0;

  if (!name || !slug) {
    return { error: "الرجاء إدخال اسم الفئة والرابط المختصر" };
  }

  const categoryData = {
    name: name.trim(),
    slug: slug.trim(),
    sort_order,
  };

  if (id) {
    const { error } = await supabase.from("categories").update(categoryData).eq("id", id);
    if (error) return { error: error.message };
  } else {
    // Check if category already exists
    const { data: existing } = await supabase.from("categories").select("id").eq("name", categoryData.name).single();
    if (existing) {
      return { error: "هذه الفئة موجودة مسبقاً" };
    }
    const { error } = await supabase.from("categories").insert(categoryData);
    if (error) return { error: error.message };
  }

  revalidatePath("/", "layout");
  return { success: true };
}

export async function deleteCategory(id: string) {
  await checkAuth();
  const supabase = await createServerClient();
  
  // Note: We don't delete projects, but if we delete a category, 
  // Supabase might set project.category_id to NULL if there's a ON DELETE SET NULL constraint.
  // We'll proceed with deletion.
  const { error } = await supabase.from("categories").delete().eq("id", id);
  if (error) return { error: error.message };

  revalidatePath("/", "layout");
  return { success: true };
}
