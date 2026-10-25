"use server";

import { revalidatePath } from "next/cache";
import { createServerClient, checkAuth } from "@/lib/supabase/server";

export async function saveProject(formData: FormData) {
  await checkAuth();
  const supabase = await createServerClient();

  const id = formData.get("id") as string | null;
  const title = formData.get("title") as string;
  const slug = formData.get("slug") as string;
  const category_id = formData.get("category_id") as string;
  const location = formData.get("location") as string;
  const client = formData.get("client") as string;
  const duration = formData.get("duration") as string;
  const area = formData.get("area") as string;
  const floors = formData.get("floors") as string;
  const year = formData.get("year") as string;
  const description = formData.get("description") as string;
  const is_featured = formData.get("is_featured") === "true";
  const is_published = formData.get("is_published") === "true";
  const attachment_file = formData.get("attachment_file") as string;
  const attachment_label = (formData.get("attachment_label") as string) || "";
  // Attachment file handling
  let finalAttachmentFile = (formData.get("attachment_file") as string) || "";
  // Strip any accidental local file: URI
  if (finalAttachmentFile.startsWith("file:")) {
    finalAttachmentFile = "";
  }

  const attachmentUpload = formData.get("attachment_upload") as File | null;
  if (attachmentUpload && attachmentUpload.size > 0) {
    const ext = (attachmentUpload.name.split(".").pop() || "pdf").toLowerCase().replace(/[^a-z0-9]/g, "");
    const fileName = `attach_${Date.now()}_${Math.random().toString(36).substring(2, 7)}.${ext}`;
    const arrayBuffer = await attachmentUpload.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    const contentType = attachmentUpload.type || "application/pdf";

    const { error: uploadError } = await supabase.storage
      .from("projects")
      .upload(fileName, buffer, { contentType, upsert: true });

    if (!uploadError) {
      const { data: publicUrlData } = supabase.storage.from("projects").getPublicUrl(fileName);
      finalAttachmentFile = publicUrlData.publicUrl;
    } else {
      console.error("[saveProject] attachment upload error:", uploadError);
    }
  }

  // Comma separated images mapping
  const imagesRaw = formData.get("images") as string;
  const images = imagesRaw ? imagesRaw.split(",").map((s) => s.trim()).filter((s) => s && !s.startsWith("file:")) : [];

  // Direct image files upload
  const uploadedImageFiles = formData.getAll("image_files") as File[];
  const uploadedImageUrls: string[] = [];

  for (const imgFile of uploadedImageFiles) {
    if (imgFile && imgFile.size > 0) {
      const ext = (imgFile.name.split(".").pop() || "jpg").toLowerCase().replace(/[^a-z0-9]/g, "");
      const fileName = `img_${Date.now()}_${Math.random().toString(36).substring(2, 7)}.${ext}`;
      const arrayBuffer = await imgFile.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      const contentType = imgFile.type || "image/jpeg";

      const { error: uploadError } = await supabase.storage
        .from("projects")
        .upload(fileName, buffer, { contentType, upsert: true });

      if (!uploadError) {
        const { data: publicUrlData } = supabase.storage.from("projects").getPublicUrl(fileName);
        uploadedImageUrls.push(publicUrlData.publicUrl);
      } else {
        console.error("[saveProject] image upload error:", uploadError);
      }
    }
  }

  const finalImages = [...images, ...uploadedImageUrls];
  
  // Scope lines
  const scopeRaw = formData.get("scope") as string;
  const scope = scopeRaw ? scopeRaw.split("\n").map((s) => s.trim()).filter(Boolean) : [];

  if (!title || !slug || !category_id) {
    return { error: "الرجاء التأكد من إدخال العنوان والرابط المختصر والفئة" };
  }

  const projectData = {
    title,
    slug,
    category_id,
    location,
    client,
    duration,
    area,
    floors,
    year,
    description,
    images: finalImages,
    scope,
    attachment_file: finalAttachmentFile || null,
    attachment_label: attachment_label || "",
    is_featured,
    is_published,
    updated_at: new Date().toISOString(),
  };

  if (id) {
    const { error } = await supabase.from("projects").update(projectData).eq("id", id);
    if (error) return { error: error.message };
  } else {
    const { error } = await supabase.from("projects").insert(projectData);
    if (error) return { error: error.message };
  }

  revalidatePath("/", "layout");
  revalidatePath("/projects");
  revalidatePath(`/projects/${encodeURIComponent(slug)}`);
  revalidatePath("/dashboard/projects");
  return { success: true };
}

export async function deleteProject(id: string) {
  await checkAuth();
  const supabase = await createServerClient();
  const { error } = await supabase.from("projects").delete().eq("id", id);
  if (error) return { error: error.message };

  revalidatePath("/", "layout");
  return { success: true };
}
