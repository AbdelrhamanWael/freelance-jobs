"use server";

import { revalidatePath, revalidateTag } from "next/cache";
import { createServerClient, checkAuth } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export type SettingsFormState = {
  success?: boolean;
  error?: string;
};

export async function saveSettings(
  prevState: SettingsFormState,
  formData: FormData
): Promise<SettingsFormState> {
  try {
    await checkAuth();
    const supabase = await createServerClient();

    const primary_color = (formData.get("primary_color") as string || "").trim();
    const secondary_color = (formData.get("secondary_color") as string || "").trim();
    const accent_color = (formData.get("accent_color") as string || "").trim();
    const is_blog_enabled = formData.get("is_blog_enabled") === "true";
    const company_name = (formData.get("company_name") as string) || "";
    const contact_email = (formData.get("contact_email") as string) || "";
    const phone = (formData.get("phone") as string) || "";
    const address = (formData.get("address") as string) || "";
    const working_hours = (formData.get("working_hours") as string) || "";
    const instagram = (formData.get("instagram") as string) || "";
    const twitter = (formData.get("twitter") as string) || "";
    const whatsapp = (formData.get("whatsapp") as string) || "";
    const footer_description = (formData.get("footer_description") as string) || "";
    const trust_enabled = formData.get("content_trust_enabled") as string | null;

    let logo_url = (formData.get("logo_url") as string) || "";
    const logoFile = formData.get("logo_file") as File | null;
    const font_scale = (formData.get("font_scale") as string) || "normal";
    let hero_bg_image = (formData.get("hero_bg_image") as string) || "";
    const heroBgFile = formData.get("hero_bg_file") as File | null;

    // Validate hex colors
    const hexRegex = /^#[0-9A-Fa-f]{6}$/;
    if (!hexRegex.test(primary_color) || !hexRegex.test(secondary_color) || !hexRegex.test(accent_color)) {
      return { error: "الألوان يجب أن تكون بصيغة Hex صحيحة مثل #004B4B" };
    }

    // Handle logo file upload
    if (logoFile && logoFile.size > 0) {
      const ext = (logoFile.name.split(".").pop() || "png").toLowerCase().replace(/[^a-z0-9]/g, "");
      const fileName = `logo_${Date.now()}_${Math.random().toString(36).substring(2, 7)}.${ext}`;
      const arrayBuffer = await logoFile.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      const contentType = logoFile.type || (ext === "png" ? "image/png" : "image/jpeg");

      const { error: uploadError } = await supabase.storage
        .from("blogs")
        .upload(fileName, buffer, { contentType, upsert: true });

      if (uploadError) {
        console.error("[saveSettings] Logo upload failed:", uploadError);
        return { error: "فشل رفع الشعار إلى وحدة التخزين: " + uploadError.message };
      }

      const { data: publicUrlData } = supabase.storage.from("blogs").getPublicUrl(fileName);
      logo_url = publicUrlData.publicUrl;
    }

    // Handle hero background file upload
    if (heroBgFile && heroBgFile.size > 0) {
      const ext = (heroBgFile.name.split(".").pop() || "jpg").toLowerCase().replace(/[^a-z0-9]/g, "");
      const fileName = `hero_bg_${Date.now()}_${Math.random().toString(36).substring(2, 7)}.${ext}`;
      const arrayBuffer = await heroBgFile.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      const contentType = heroBgFile.type || (ext === "png" ? "image/png" : "image/jpeg");

      const { error: uploadError } = await supabase.storage
        .from("blogs")
        .upload(fileName, buffer, { contentType, upsert: true });

      if (uploadError) {
        console.error("[saveSettings] Hero background upload failed:", uploadError);
        return { error: "فشل رفع صورة الخلفية إلى وحدة التخزين: " + uploadError.message };
      }

      const { data: publicUrlData } = supabase.storage.from("blogs").getPublicUrl(fileName);
      hero_bg_image = publicUrlData.publicUrl;
    }

    // Get existing settings row ID
    const { data: existing } = await supabase
      .from("site_settings")
      .select("id, logo_url, hero_bg_image")
      .limit(1)
      .single();

    // Handle hero background: if a file was uploaded, use it. Otherwise use the submitted text input.
    const finalHeroBgImage = hero_bg_image;
    const finalLogoUrl = logo_url || (existing?.logo_url || "/logo-horizontal.png");

    const payload: any = {
      primary_color,
      secondary_color,
      accent_color,
      is_blog_enabled,
      company_name,
      contact_email,
      phone,
      address,
      working_hours,
      instagram,
      twitter,
      whatsapp,
      footer_description,
      font_scale,
      logo_url: finalLogoUrl,
      hero_bg_image: finalHeroBgImage,
    };

    if (!existing) {
      const { error } = await supabase.from("site_settings").insert(payload);
      if (error) return { error: "فشل حفظ الإعدادات: " + error.message };
    } else {
      const { error } = await supabase
        .from("site_settings")
        .update(payload)
        .eq("id", existing.id);
      if (error) return { error: "فشل تحديث الإعدادات: " + error.message };
    }

    // Also sync hero_bg_image with page_content for consistency
    await supabase
      .from("page_content")
      .upsert(
        { key: "hero_bg_image", value: finalHeroBgImage, section: "hero", label: "صورة خلفية الواجهة (رابط بانر أو صورة)" },
        { onConflict: "key" }
      );

    if (trust_enabled !== null) {
      const { error: contentError } = await supabase
        .from("page_content")
        .upsert(
          { key: "trust_enabled", value: trust_enabled, section: "trust", label: "إظهار أرقام الإنجازات" },
          { onConflict: "key" }
        );
      if (contentError) {
        console.error("[saveSettings] Error saving trust_enabled:", contentError.message);
      }
    }

    // Invalidate pages so layout.tsx picks up new colors immediately
    // @ts-expect-error Next.js 16 types bug
    revalidateTag("site_settings");
    revalidatePath("/", "layout");
    revalidatePath("/projects");
    revalidatePath("/blog");

    return { success: true };
  } catch (err: any) {
    console.error("[saveSettings] Unexpected error:", err);
    return { error: "حدث خطأ أثناء معالجة الإعدادات: " + (err.message || String(err)) };
  }
}

export async function savePageContent(
  prevState: SettingsFormState,
  formData: FormData
): Promise<SettingsFormState> {
  try {
    await checkAuth();
    const supabase = await createServerClient();

    const updates: Array<{ key: string; value: string }> = [];

    formData.forEach((value, key) => {
      if (key.startsWith("content_")) {
        const contentKey = key.replace("content_", "");
        updates.push({ key: contentKey, value: value as string });
      }
    });

    for (const update of updates) {
      const { data: existing } = await supabase
        .from("page_content")
        .select("id")
        .eq("key", update.key)
        .maybeSingle();

      if (existing) {
        const { error } = await supabase
          .from("page_content")
          .update({ value: update.value, updated_at: new Date().toISOString() })
          .eq("key", update.key);

        if (error) {
          return { error: `فشل تحديث "${update.key}": ` + error.message };
        }
      } else {
        const { error } = await supabase
          .from("page_content")
          .insert({
            key: update.key,
            value: update.value,
            label: update.key,
            updated_at: new Date().toISOString(),
          });

        if (error) {
          return { error: `فشل إضافة "${update.key}": ` + error.message };
        }
      }
    }

    // Invalidate all pages so content updates propagate
    // @ts-expect-error Next.js 16 types bug
    revalidateTag("page_content");
    revalidatePath("/", "layout");

    return { success: true };
  } catch (err: any) {
    console.error("[savePageContent] Error:", err);
    return { error: "حدث خطأ أثناء حفظ المحتوى: " + (err.message || String(err)) };
  }
}
