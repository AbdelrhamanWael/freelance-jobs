"use server";

import { revalidatePath } from "next/cache";
import { createServerClient, checkAuth } from "@/lib/supabase/server";

export async function saveStat(formData: FormData) {
  await checkAuth();
  const supabase = await createServerClient();

  const id = formData.get("id") as string | null;
  const label = (formData.get("label") as string).trim();
  const value = (formData.get("value") as string).trim();
  const sort_order = parseInt(formData.get("sort_order") as string, 10) || 99;
  const is_visible = formData.get("is_visible") !== "false";

  if (!label || !value) {
    return { error: "الرجاء إدخال اسم الخانة والقيمة" };
  }

  const payload = { label, value, sort_order, is_visible };

  if (id) {
    const { error } = await supabase.from("stats").update(payload).eq("id", id);
    if (error) return { error: error.message };
  } else {
    const { error } = await supabase.from("stats").insert(payload);
    if (error) return { error: error.message };
  }

  revalidatePath("/", "layout");
  return { success: true };
}

export async function deleteStat(id: string) {
  await checkAuth();
  const supabase = await createServerClient();
  const { error } = await supabase.from("stats").delete().eq("id", id);
  if (error) return { error: error.message };
  revalidatePath("/", "layout");
  return { success: true };
}

export async function getStats() {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from("stats")
      .select("*")
      .eq("is_visible", true)
      .order("sort_order", { ascending: true });
    if (error || !data) return [];
    return data as { id: string; label: string; value: string; sort_order: number; is_visible: boolean }[];
  } catch {
    return [];
  }
}
