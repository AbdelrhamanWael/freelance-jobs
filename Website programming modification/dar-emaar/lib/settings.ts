/**
 * lib/settings.ts
 * Fetch site_settings from Supabase.
 * Used in layout.tsx to inject CSS variables.
 * Cached per-request (Next.js default for Server Components).
 */

import { createServerClient } from "@/lib/supabase/server";

export type SiteSettings = {
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  is_blog_enabled: boolean;
  company_name: string;
  contact_email: string;
  phone: string;
  address: string;
  working_hours: string;
  instagram: string;
  twitter: string;
  whatsapp: string;
  footer_description: string;
  logo_url: string;
  font_scale: string;
  hero_bg_image: string;
};

const DEFAULT_SETTINGS: SiteSettings = {
  primary_color: "#004B4B",
  secondary_color: "#F9F3EC",
  accent_color: "#6C6D71",
  is_blog_enabled: false,
  company_name: "دار اعمار الغربية",
  contact_email: "info@daremmar.com",
  phone: "+966 50 000 0000",
  address: "المملكة العربية السعودية — جدة، حي الواجهة",
  working_hours: "السبت – الخميس: 8ص – 6م",
  instagram: "#",
  twitter: "#",
  whatsapp: "https://wa.me/966500000000",
  footer_description: "شركة رائدة في مجال المقاولات العامة تأسست عام 2009، تقدم حلولاً إنشائية متكاملة بجودة عالية وكفاءة محترفة.",
  logo_url: "/logo-horizontal.png",
  font_scale: "normal",
  hero_bg_image: "",
};

/**
 * Fetch site settings — cached for 60 seconds so the layout isn't
 * hitting Supabase on every single request.
 * Revalidates automatically when settings are saved from dashboard.
 */
export async function getSettings(): Promise<SiteSettings> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from("site_settings")
      .select("*")
      .limit(1)
      .single();

    if (error || !data) {
      console.warn("[settings] Falling back to defaults:", error?.message);
      return DEFAULT_SETTINGS;
    }

    // Validate stored colors — if they look wrong, fall back to defaults
    const hexRegex = /^#[0-9A-Fa-f]{6}$/;
    const primaryOk = hexRegex.test(data.primary_color);
    const secondaryOk = hexRegex.test(data.secondary_color);
    const accentOk = hexRegex.test(data.accent_color);

    return {
      primary_color: (primaryOk ? data.primary_color : null) || DEFAULT_SETTINGS.primary_color,
      secondary_color: (secondaryOk ? data.secondary_color : null) || DEFAULT_SETTINGS.secondary_color,
      accent_color: (accentOk ? data.accent_color : null) || DEFAULT_SETTINGS.accent_color,
      is_blog_enabled: data.is_blog_enabled ?? false,
      company_name: data.company_name || DEFAULT_SETTINGS.company_name,
      contact_email: data.contact_email || DEFAULT_SETTINGS.contact_email,
      phone: data.phone || DEFAULT_SETTINGS.phone,
      address: data.address || DEFAULT_SETTINGS.address,
      working_hours: data.working_hours || DEFAULT_SETTINGS.working_hours,
      instagram: data.instagram || DEFAULT_SETTINGS.instagram,
      twitter: data.twitter || DEFAULT_SETTINGS.twitter,
      whatsapp: data.whatsapp || DEFAULT_SETTINGS.whatsapp,
      footer_description: data.footer_description || DEFAULT_SETTINGS.footer_description,
      logo_url: data.logo_url || DEFAULT_SETTINGS.logo_url,
      font_scale: data.font_scale || DEFAULT_SETTINGS.font_scale,
      hero_bg_image: data.hero_bg_image || DEFAULT_SETTINGS.hero_bg_image,
    };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

/**
 * Compute whether a hex color is "dark" (luminance < 0.4).
 * Used to decide button text color (white vs dark) for contrast.
 */
export function isDarkColor(hex: string): boolean {
  const clean = hex.replace("#", "");
  if (clean.length !== 6) return true;
  const r = parseInt(clean.slice(0, 2), 16) / 255;
  const g = parseInt(clean.slice(2, 4), 16) / 255;
  const b = parseInt(clean.slice(4, 6), 16) / 255;
  // Relative luminance (WCAG formula)
  const toLinear = (c: number) => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  const luminance = 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
  return luminance < 0.4;
}
