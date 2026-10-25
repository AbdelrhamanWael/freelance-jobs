"use server";

import { revalidatePath } from "next/cache";
import { createServerClient, checkAuth } from "@/lib/supabase/server";

export async function saveClient(prevState: any, formData: FormData) {
  await checkAuth();
  const supabase = await createServerClient();

  const id = formData.get("id") as string | null;
  const name = formData.get("name") as string;
  let logo_url = formData.get("logo_url") as string;
  const logoFile = formData.get("logo_file") as File | null;
  const sort_order = parseInt(formData.get("sort_order") as string) || 0;
  const is_published = formData.get("is_published") === "true";

  if (!name) {
    return { error: "اسم العميل مطلوب" };
  }

  // Handle file upload
  if (logoFile && logoFile.size > 0) {
    const fileExt = logoFile.name.split('.').pop();
    const fileName = `${Math.random().toString(36).substring(2, 15)}_${Date.now()}.${fileExt}`;
    const { data: uploadData, error: uploadError } = await supabase.storage
      .from("clients")
      .upload(fileName, logoFile);

    if (uploadError) {
      return { error: `فشل رفع الشعار: ${uploadError.message}` };
    }

    const { data: publicUrlData } = supabase.storage.from("clients").getPublicUrl(fileName);
    logo_url = publicUrlData.publicUrl;
  }

  const clientData = {
    name,
    logo_url,
    sort_order,
    is_published,
  };

  if (id && id !== "new") {
    const { error } = await supabase.from("clients").update(clientData).eq("id", id);
    if (error) return { error: error.message };
  } else {
    const { error } = await supabase.from("clients").insert(clientData);
    if (error) return { error: error.message };
  }

  revalidatePath("/", "layout");
  return { success: true };
}

export async function deleteClient(id: string) {
  await checkAuth();
  const supabase = await createServerClient();
  const { error } = await supabase.from("clients").delete().eq("id", id);
  if (error) return { error: error.message };

  revalidatePath("/", "layout");
  return { success: true };
}
