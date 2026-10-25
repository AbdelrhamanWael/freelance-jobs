import { createServerClient } from "@/lib/supabase/server";
import { getSettings } from "@/lib/settings";
import SettingsForm from "@/components/dashboard/SettingsForm";

export const metadata = {
  title: "الإعدادات — لوحة التحكم",
};

export default async function SettingsPage({
  searchParams,
}: {
  searchParams?: Promise<{ tab?: string }>;
}) {
  const resolvedParams = searchParams ? await searchParams : {};
  const defaultTab = resolvedParams?.tab;

  const supabase = await createServerClient();
  const settings = await getSettings();

  // Fetch all page content rows for the editor
  const { data: dbRows = [] } = await supabase
    .from("page_content")
    .select("key, value, label, section")
    .order("section");

  const expectedRows = [
    { key: "header_cta_text", label: "نص الزر في الشريط العلوي", section: "header" },
    { key: "hero_title", label: "العنوان الرئيسي", section: "hero" },
    { key: "hero_title_accent", label: "النص البارز في العنوان", section: "hero" },
    { key: "hero_badge", label: "نص الشارة الصغيرة", section: "hero" },
    { key: "hero_subtitle", label: "الوصف", section: "hero" },
    { key: "hero_cta", label: "نص زر اتخاذ الإجراء", section: "hero" },
    { key: "hero_phone_label", label: "نص زر الاتصال في الهيرو (مثال: تحدث مع الفريق الهندسي)", section: "hero" },
    { key: "hero_bg_image", label: "صورة خلفية الواجهة (رابط بانر أو صورة)", section: "hero" },
    // Services Section
    { key: "services_badge", label: "شارة قسم الخدمات (أعلى الهيدلاين)", section: "services" },
    { key: "services_title", label: "العنوان الرئيسي (هيد لاين قسم الخدمات)", section: "services" },
    { key: "services_subtitle", label: "الوصف التمهيدي لقسم الخدمات", section: "services" },
    { key: "service_1_title", label: "الخدمة الأولى: العنوان", section: "services" },
    { key: "service_1_desc", label: "الخدمة الأولى: الوصف الشامل", section: "services" },
    { key: "service_1_highlights", label: "الخدمة الأولى: خانات ومميزات الخدمة (سطر لكل ميزة)", section: "services" },
    { key: "service_2_title", label: "الخدمة الثانية: العنوان", section: "services" },
    { key: "service_2_desc", label: "الخدمة الثانية: الوصف الشامل", section: "services" },
    { key: "service_2_highlights", label: "الخدمة الثانية: خانات ومميزات الخدمة (سطر لكل ميزة)", section: "services" },
    { key: "service_3_title", label: "الخدمة الثالثة: العنوان", section: "services" },
    { key: "service_3_desc", label: "الخدمة الثالثة: الوصف الشامل", section: "services" },
    { key: "service_3_highlights", label: "الخدمة الثالثة: خانات ومميزات الخدمة (سطر لكل ميزة)", section: "services" },
    { key: "services_footer_text", label: "النص التوضيحي الإضافي أسفل كروت الخدمات", section: "services" },
    { key: "services_footer_cta", label: "نص رابط التواصل الإضافي في الأسفل", section: "services" },
    // Projects Section & Page
    { key: "projects_badge", label: "شارة قسم المشاريع (أعلى الهيدلاين)", section: "projects" },
    { key: "projects_title", label: "العنوان الرئيسي لقسم المشاريع (الهيد لاين)", section: "projects" },
    { key: "projects_subtitle", label: "الوصف التمهيدي لقسم المشاريع", section: "projects" },
    { key: "projects_featured_label", label: "شارة المشروع المميز في البطاقة الكبيرة", section: "projects" },
    { key: "projects_featured_cta", label: "نص زر اتخاذ الإجراء في المشروع المميز", section: "projects" },
    { key: "projects_view_all_cta", label: "نص زر تصفح جميع المشاريع في الأسفل", section: "projects" },
    { key: "projects_page_badge", label: "شارة رأس صفحة معرض المشاريع", section: "projects" },
    { key: "projects_page_title", label: "العنوان الرئيسي لصفحة المشاريع", section: "projects" },
    { key: "projects_page_subtitle", label: "الوصف التمهيدي لصفحة المشاريع", section: "projects" },
    { key: "projects_page_cta_title", label: "عنوان صندوق التواصل أسفل صفحة المشاريع", section: "projects" },
    { key: "projects_page_cta_desc", label: "وصف صندوق التواصل أسفل صفحة المشاريع", section: "projects" },
    { key: "projects_page_cta_button", label: "نص زر التواصل أسفل صفحة المشاريع", section: "projects" },
    { key: "trust_years", label: "عدد سنوات الخبرة", section: "trust" },
    { key: "trust_projects", label: "عدد المشاريع المنجزة", section: "trust" },
    { key: "trust_clients", label: "عدد العملاء", section: "trust" },
    { key: "trust_satisfaction", label: "معدل رضا العملاء (%)", section: "trust" },
    { key: "phone_number", label: "رقم الجوال", section: "contact" },
    { key: "email", label: "البريد الإلكتروني", section: "contact" },
    { key: "company_address", label: "عنوان الشركة", section: "contact" },
    { key: "working_hours", label: "ساعات العمل", section: "contact" },
    { key: "form_section_title", label: "عنوان نموذج التواصل", section: "form" },
    { key: "form_section_sub", label: "وصف نموذج التواصل", section: "form" },
    // Contact services list (1 to 6 items)
    { key: "contact_services_list", label: "فئات الخدمة المطلوبة في نموذج تواصل معنا (من 1 إلى 6)", section: "contact_services" },
  ];

  // Merge DB rows with expected rows to ensure all fields are always present
  const contentMap = (dbRows || []).reduce((acc: any, row) => {
    acc[row.key] = row;
    return acc;
  }, {});

  const contentRows = expectedRows.map((expected) => ({
    ...expected,
    value: contentMap[expected.key]?.value || "",
  }));

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-black text-[#1B2A4A]">إعدادات الموقع</h1>
        <p className="text-[#64748B] text-sm mt-1">
          تحكم في ألوان الموقع ونصوصه وميزاته مباشرة من هنا
        </p>
      </div>

      <SettingsForm
        initialSettings={settings}
        contentRows={contentRows || []}
        defaultTab={defaultTab}
      />
    </div>
  );
}
