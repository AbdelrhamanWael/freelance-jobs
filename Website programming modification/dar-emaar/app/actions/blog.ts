"use server";

import { revalidatePath } from "next/cache";
import { createServerClient, checkAuth } from "@/lib/supabase/server";

export async function saveBlogPost(formData: FormData) {
  await checkAuth();
  const supabase = await createServerClient();

  const id = formData.get("id") as string | null;
  const title = formData.get("title") as string;
  const slug = formData.get("slug") as string;
  const excerpt = formData.get("excerpt") as string;
  const content = formData.get("content") as string;
  let cover_image = (formData.get("cover_image") as string) || "";
  const coverFile = formData.get("cover_file") as File | null;
  const author = (formData.get("author") as string) || "فريق دار اعمار الغربية";
  const author_title = (formData.get("author_title") as string) || "قسم الهندسة والمحتوى المعماري";
  const author_bio = (formData.get("author_bio") as string) || "نشارككم خبراتنا الميدانية وأحدث الأفكار والحلول الهندسية في مجالات المقاولات العامة والتشطيبات الفاخرة وإدارة المشاريع بالمملكة العربية السعودية.";
  const is_published = formData.get("is_published") === "true";

  if (!title || !slug) {
    return { error: "العنوان والرابط المختصر (slug) مطلوبان" };
  }

  // Handle direct file upload to 'blogs' storage bucket
  if (coverFile && coverFile.size > 0) {
    const fileExt = coverFile.name.split(".").pop() || "jpg";
    const fileName = `blog_${Math.random().toString(36).substring(2, 9)}_${Date.now()}.${fileExt}`;
    const { error: uploadError } = await supabase.storage
      .from("blogs")
      .upload(fileName, coverFile, { contentType: coverFile.type || "image/jpeg" });

    if (!uploadError) {
      const { data: publicUrlData } = supabase.storage.from("blogs").getPublicUrl(fileName);
      cover_image = publicUrlData.publicUrl;
    } else {
      console.warn("Storage upload failed, falling back to URL input:", uploadError.message);
    }
  }

  const postData = {
    title,
    slug,
    excerpt,
    content,
    cover_image,
    author,
    author_title,
    author_bio,
    is_published,
    updated_at: new Date().toISOString(),
    ...(is_published ? { published_at: new Date().toISOString() } : {}),
  };

  if (id) {
    // Update existing
    const { error } = await supabase.from("blog_posts").update(postData).eq("id", id);
    if (error) return { error: error.message };
  } else {
    // Insert new
    const { error } = await supabase.from("blog_posts").insert(postData);
    if (error) return { error: error.message };
  }

  revalidatePath("/", "layout");
  return { success: true };
}

export async function deleteBlogPost(id: string) {
  await checkAuth();
  const supabase = await createServerClient();
  const { error } = await supabase.from("blog_posts").delete().eq("id", id);
  if (error) return { error: error.message };

  revalidatePath("/", "layout");
  return { success: true };
}
