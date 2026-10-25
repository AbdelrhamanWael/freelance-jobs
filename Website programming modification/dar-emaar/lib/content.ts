/**
 * lib/content.ts
 * Fetch page_content key-value pairs from Supabase.
 * Returns a typed dictionary so components can safely access content.
 */

import { createServerClient } from "@/lib/supabase/server";

export type PageContent = {
  hero_title: string;
  hero_title_accent: string;
  hero_badge: string;
  header_cta_text: string;
  hero_subtitle: string;
  hero_cta: string;
  hero_bg_image?: string;
  hero_phone_label?: string;
  trust_enabled: string;
  trust_years: string;
  trust_projects: string;
  trust_clients: string;
  trust_satisfaction: string;
  phone_number: string;
  company_address: string;
  email: string;
  working_hours: string;
  form_section_title: string;
  form_section_sub: string;
  // Services Section
  services_badge?: string;
  services_title?: string;
  services_subtitle?: string;
  service_1_title?: string;
  service_1_desc?: string;
  service_1_highlights?: string;
  service_2_title?: string;
  service_2_desc?: string;
  service_2_highlights?: string;
  service_3_title?: string;
  service_3_desc?: string;
  service_3_highlights?: string;
  services_footer_text?: string;
  services_footer_cta?: string;
  // Projects Section & Page
  projects_badge?: string;
  projects_title?: string;
  projects_subtitle?: string;
  projects_featured_label?: string;
  projects_featured_cta?: string;
  projects_view_all_cta?: string;
  projects_page_badge?: string;
  projects_page_title?: string;
  projects_page_subtitle?: string;
  projects_page_cta_title?: string;
  projects_page_cta_desc?: string;
  projects_page_cta_button?: string;
  // Contact Form Services List (JSON array of strings, 1 to 6 items)
  contact_services_list?: string;
  [key: string]: string | undefined; // allow extra keys without TS errors
};

export const DEFAULT_CONTACT_SERVICES: string[] = [
  "التصميم والبناء",
  "اعمال الحفر والاحلال",
  "الهيكل الانشائي",
  "الالكتروميكانيك",
  "التشطيبات الداخلية والخارجية",
];

const DEFAULT_CONTENT: PageContent = {
  hero_title: "شركاؤك في البناء",
  hero_title_accent: "من الفكرة إلى التسليم",
  hero_badge: "أكثر من 15 عاماً من الثقة والجودة",
  header_cta_text: "طلب استشارة",
  hero_subtitle: "نقدم حلولاً متكاملة في المقاولات والتشطيبات وإدارة المشاريع بمعايير جودة عالية وكفاءة محترفة",
  hero_cta: "احصل على عرض سعر مجاني",
  hero_bg_image: "",
  hero_phone_label: "تحدث مع الفريق الهندسي",
  trust_enabled: "true",
  trust_years: "15",
  trust_projects: "200",
  trust_clients: "50",
  trust_satisfaction: "98",
  phone_number: "+966500000000",
  company_address: "المملكة العربية السعودية — جدة، حي الواجهة",
  email: "info@daremmar.com",
  working_hours: "السبت – الخميس: 8ص – 6م",
  form_section_title: "احصل على عرض سعر مجاني",
  form_section_sub: "نرد خلال 24 ساعة — استشارة أولى بدون أي التزام",
  contact_services_list: JSON.stringify(DEFAULT_CONTACT_SERVICES),
  // Services Defaults
  services_badge: "خدماتنا",
  services_title: "ماذا نقدم لك؟",
  services_subtitle: "نقدم مجموعة متكاملة من الخدمات الإنشائية تحت سقف واحد — لضمان تجربة بناء سلسة وبلا تعقيد",
  service_1_title: "التصميم والبناء",
  service_1_desc: "تصميم معماري متكامل مع هندسة متخصصة وتنفيذ بجودة عالية وتكلفة تنافسية، من رسم المخططات حتى استلام المفتاح.",
  service_1_highlights: "تصميم معماري احترافي\nإشراف هندسي متكامل\nمواد بناء عالية الجودة",
  service_2_title: "التشطيبات الداخلية",
  service_2_desc: "تشطيبات فاخرة تناسب ذوقك وميزانيتك — من الجبس والدهانات حتى الأرضيات والأسقف المعلقة بأعلى المعايير.",
  service_2_highlights: "أسقف جبسية وديكور\nدهانات وورق جدران\nأرضيات وبلاط فاخر",
  service_3_title: "إدارة المشاريع",
  service_3_desc: "إدارة احترافية كاملة للمشاريع من التخطيط والجدولة الزمنية حتى التسليم النهائي مع ضمان الالتزام بالموعد والميزانية.",
  service_3_highlights: "جدولة زمنية دقيقة\nتقارير دورية شاملة\nتنسيق كامل مع المقاولين",
  services_footer_text: "نقدم أيضاً: أعمال الحفر والردم، البنية التحتية، الطاقة المتجددة، خدمات لوجستية، وأكثر من 10 خدمات متخصصة أخرى.",
  services_footer_cta: "تواصل معنا لمعرفة كل خدماتنا ←",
  // Projects Defaults
  projects_badge: "مشاريعنا",
  projects_title: "مشاريع نفخر بتنفيذها",
  projects_subtitle: "نفخر بتسليم مشاريع تتجاوز توقعات عملائنا في الجودة والالتزام بالمواعيد",
  projects_featured_label: "مشروع مميز",
  projects_featured_cta: "أريد مشروعاً مشابهاً",
  projects_view_all_cta: "عرض جميع المشاريع",
  projects_page_badge: "معرض الأعمال",
  projects_page_title: "مشاريعنا",
  projects_page_subtitle: "أكثر من 200 مشروع منجز عبر مختلف القطاعات — تصفح أبرز إنجازاتنا",
  projects_page_cta_title: "هل لديك مشروع مماثل؟",
  projects_page_cta_desc: "احصل على استشارة مجانية من فريق خبرائنا",
  projects_page_cta_button: "طلب استشارة مجانية",
};

/**
 * Parses and returns the list of contact services (1 to 6 items).
 */
export function getContactServices(content?: PageContent | null): string[] {
  if (!content?.contact_services_list) {
    return DEFAULT_CONTACT_SERVICES;
  }
  try {
    const parsed = JSON.parse(content.contact_services_list);
    if (Array.isArray(parsed) && parsed.length > 0) {
      const cleaned = parsed
        .map((s) => (typeof s === "string" ? s.trim() : ""))
        .filter(Boolean);
      if (cleaned.length > 0) {
        return cleaned.slice(0, 6);
      }
    }
  } catch {
    const split = content.contact_services_list
      .split(/[\n,]+/)
      .map((s) => s.trim())
      .filter(Boolean);
    if (split.length > 0) {
      return split.slice(0, 6);
    }
  }
  return DEFAULT_CONTACT_SERVICES;
}

/**
 * Fetch all page content rows and convert to a typed dictionary.
 */
export async function getPageContent(): Promise<PageContent> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from("page_content")
      .select("key, value");

    if (error || !data) {
      console.warn("[content] DB error, using defaults");
      return DEFAULT_CONTENT;
    }

    // Convert array of {key, value} to a dictionary object
    const contentMap = data.reduce((acc, item) => {
      acc[item.key] = item.value;
      return acc;
    }, {} as Record<string, string>);

    // Merge with defaults to ensure all keys exist
    return { ...DEFAULT_CONTENT, ...contentMap } as PageContent;
  } catch (err) {
    console.error("[content] Failed to fetch content:", err);
    return DEFAULT_CONTENT;
  }
}
