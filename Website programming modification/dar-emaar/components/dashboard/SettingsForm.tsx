"use client";

import { useActionState, useState, useRef } from "react";
import { saveSettings, savePageContent, type SettingsFormState } from "@/app/actions/settings";
import type { SiteSettings } from "@/lib/settings";
import { 
  Palette, 
  FileText, 
  AlertCircle, 
  CheckCircle2, 
  Save, 
  Upload, 
  Image as ImageIcon, 
  Type, 
  Trash2, 
  RotateCcw,
  Sparkles,
  Info,
  Check,
  Loader2,
  Briefcase,
  Building2,
  Layers,
  Lock,
  Plus,
  ListOrdered
} from "lucide-react";
import { createClient } from "@/lib/supabase/client";

type ContentRow = {
  key: string;
  value: string;
  label: string;
  section: string;
};

type Props = {
  initialSettings: SiteSettings;
  contentRows: ContentRow[];
  defaultTab?: string;
};

const initialState: SettingsFormState = {};

// Group content rows by section
function groupBySection(rows: ContentRow[]) {
  return rows.reduce((acc, row) => {
    if (!acc[row.section]) acc[row.section] = [];
    acc[row.section].push(row);
    return acc;
  }, {} as Record<string, ContentRow[]>);
}

const sectionLabels: Record<string, string> = {
  header: "الشريط العلوي (الهيدر)",
  hero: "قسم الهيرو (أعلى الصفحة)",
  services: "قسم خدماتنا",
  projects: "قسم وصفحة مشاريعنا",
  trust: "أرقام الإنجازات",
  contact: "بيانات التواصل",
  form: "قسم النموذج",
  general: "عام",
};

/**
 * Client-side image compressor:
 * Shrinks huge images (e.g. 5-10MB DALL-E / phone photos) down to ~400-800KB
 * with max width 2560px and 88% quality.
 * Prevents Vercel 4.5MB Serverless limit errors and ensures instant upload.
 */
async function optimizeImageFile(file: File, maxWidth = 2560): Promise<File> {
  // If it's already a tiny file (e.g. SVG or under 800KB), return as is
  if (file.type.includes("svg") || (file.size < 800 * 1024 && !file.type.includes("png"))) {
    return file;
  }

  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (e) => {
      const img = new Image();
      img.src = e.target?.result as string;
      img.onload = () => {
        let { width, height } = img;
        if (width > maxWidth) {
          height = Math.round((height * maxWidth) / width);
          width = maxWidth;
        }

        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        if (!ctx) {
          resolve(file);
          return;
        }

        ctx.drawImage(img, 0, 0, width, height);

        // For large PNG banners, convert to high-quality JPEG to drop size by 90%
        const isPng = file.type === "image/png";
        const targetMime = (isPng && file.size > 1.5 * 1024 * 1024) ? "image/jpeg" : (file.type || "image/jpeg");
        const targetExt = targetMime === "image/jpeg" ? ".jpg" : ".png";

        canvas.toBlob(
          (blob) => {
            if (!blob || blob.size >= file.size) {
              resolve(file);
              return;
            }
            const cleanName = file.name.replace(/\.[^/.]+$/, "") + targetExt;
            const optimized = new File([blob], cleanName, { type: targetMime });
            resolve(optimized);
          },
          targetMime,
          0.88
        );
      };
      img.onerror = () => resolve(file);
    };
    reader.onerror = () => resolve(file);
  });
}

export default function SettingsForm({ initialSettings, contentRows, defaultTab }: Props) {
  const [settingsState, settingsAction, settingsPending] = useActionState(saveSettings, initialState);
  const [contentState, contentAction, contentPending] = useActionState(savePageContent, initialState);

  const [activeTab, setActiveTab] = useState<"colors" | "services" | "projects" | "contact_services" | "content">(() => {
    if (defaultTab && ["colors", "services", "projects", "contact_services", "content"].includes(defaultTab as any)) {
      return defaultTab as any;
    }
    return "colors";
  });

  // Contact services list state (1 to 6 slots)
  const initialContactServicesRaw = contentRows.find((r) => r.key === "contact_services_list")?.value;
  const parseServices = (raw?: string): string[] => {
    if (!raw) {
      return [
        "التصميم والبناء",
        "اعمال الحفر والاحلال",
        "الهيكل الانشائي",
        "الالكتروميكانيك",
        "التشطيبات الداخلية والخارجية",
      ];
    }
    try {
      const arr = JSON.parse(raw);
      if (Array.isArray(arr) && arr.length > 0) {
        return arr.map((s) => String(s).trim()).filter(Boolean).slice(0, 6);
      }
    } catch {}
    const split = raw.split(/[\n,]+/).map((s) => s.trim()).filter(Boolean);
    if (split.length > 0) return split.slice(0, 6);
    return [
      "التصميم والبناء",
      "اعمال الحفر والاحلال",
      "الهيكل الانشائي",
      "الالكتروميكانيك",
      "التشطيبات الداخلية والخارجية",
    ];
  };

  const [contactServices, setContactServices] = useState<string[]>(() => parseServices(initialContactServicesRaw));

  const handleServiceChange = (index: number, val: string) => {
    setContactServices((prev) => {
      const next = [...prev];
      next[index] = val;
      return next;
    });
  };

  const handleAddService = () => {
    if (contactServices.length >= 6) return;
    setContactServices((prev) => [...prev, ""]);
  };

  const handleRemoveService = (index: number) => {
    if (contactServices.length <= 1) return;
    setContactServices((prev) => prev.filter((_, i) => i !== index));
  };

  const handleResetServices = () => {
    setContactServices([
      "التصميم والبناء",
      "اعمال الحفر والاحلال",
      "الهيكل الانشائي",
      "الالكتروميكانيك",
      "التشطيبات الداخلية والخارجية",
    ]);
  };

  const [previewColors, setPreviewColors] = useState({
    primary: initialSettings.primary_color,
    secondary: initialSettings.secondary_color,
    accent: initialSettings.accent_color,
  });

  // Media and font controls
  const [logoPreview, setLogoPreview] = useState<string>(initialSettings.logo_url || "/logo-horizontal.png");
  const [logoUrlInput, setLogoUrlInput] = useState<string>(initialSettings.logo_url || "/logo-horizontal.png");
  const [logoNotice, setLogoNotice] = useState<string>("");
  const [logoOptimizing, setLogoOptimizing] = useState(false);
  const logoFileInputRef = useRef<HTMLInputElement>(null);

  const [heroBgPreview, setHeroBgPreview] = useState<string>(initialSettings.hero_bg_image || "");
  const [heroBgInput, setHeroBgInput] = useState<string>(initialSettings.hero_bg_image || "");
  const [heroNotice, setHeroNotice] = useState<string>("");
  const [heroOptimizing, setHeroOptimizing] = useState(false);
  const heroBgFileInputRef = useRef<HTMLInputElement>(null);

  const [fontScale, setFontScale] = useState<string>(initialSettings.font_scale || "normal");

  // Password change state
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordMsg, setPasswordMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const handlePasswordChange = async () => {
    setPasswordMsg(null);
    if (!newPassword || newPassword.length < 6) {
      setPasswordMsg({ type: "error", text: "كلمة المرور يجب أن لا تقل عن 6 أحرف أو أرقام." });
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordMsg({ type: "error", text: "كلمة المرور وتأكيدها غير متطابقين." });
      return;
    }
    setPasswordLoading(true);
    try {
      const supabase = createClient();
      const { error } = await supabase.auth.updateUser({ password: newPassword });
      if (error) {
        setPasswordMsg({ type: "error", text: error.message || "حدث خطأ أثناء تحديث كلمة المرور." });
      } else {
        setPasswordMsg({ type: "success", text: "✓ تم تحديث كلمة المرور بنجاح! يمكنك استخدامها لتسجيل الدخول مستقبلاً." });
        setNewPassword("");
        setConfirmPassword("");
      }
    } catch {
      setPasswordMsg({ type: "error", text: "فشل في تحديث كلمة المرور." });
    } finally {
      setPasswordLoading(false);
    }
  };

  const grouped = groupBySection(contentRows);

  // Live preview: update CSS vars when color pickers change
  const updatePreview = (key: "primary" | "secondary" | "accent", value: string) => {
    setPreviewColors((prev) => ({ ...prev, [key]: value }));
    const varMap = { primary: "--color-primary", secondary: "--color-secondary", accent: "--color-accent" };
    document.documentElement.style.setProperty(varMap[key], value);
  };

  const handleLogoFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setLogoPreview(URL.createObjectURL(file));
      setLogoOptimizing(true);
      setLogoNotice("جارٍ تحسين الصورة وضغطها لسرعة التحميل...");
      try {
        const optimized = await optimizeImageFile(file, 1200);
        if (logoFileInputRef.current && typeof DataTransfer !== "undefined") {
          const dt = new DataTransfer();
          dt.items.add(optimized);
          logoFileInputRef.current.files = dt.files;
        }
        setLogoNotice(`✓ تم تحسين الشعار (${(optimized.size / 1024).toFixed(0)} كيلوبايت) - جاهز للحفظ.`);
      } catch {
        setLogoNotice("");
      } finally {
        setLogoOptimizing(false);
      }
    }
  };

  const handleResetLogo = () => {
    const defaultLogo = "/logo-horizontal.png";
    setLogoPreview(defaultLogo);
    setLogoUrlInput(defaultLogo);
    setLogoNotice("");
    if (logoFileInputRef.current) {
      logoFileInputRef.current.value = "";
    }
  };

  const handleHeroBgFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setHeroBgPreview(URL.createObjectURL(file));
      setHeroOptimizing(true);
      setHeroNotice("جارٍ تحسين صورة الخلفية وضغطها لتناسب سرعة الموقع...");
      try {
        const optimized = await optimizeImageFile(file, 2560);
        if (heroBgFileInputRef.current && typeof DataTransfer !== "undefined") {
          const dt = new DataTransfer();
          dt.items.add(optimized);
          heroBgFileInputRef.current.files = dt.files;
        }
        setHeroNotice(`✓ تم تحسين وضغط الصورة بنجاح (${(optimized.size / 1024).toFixed(0)} كيلوبايت) - جاهزة للحفظ السريع.`);
      } catch {
        setHeroNotice("");
      } finally {
        setHeroOptimizing(false);
      }
    }
  };

  const handleClearHeroBg = () => {
    setHeroBgPreview("");
    setHeroBgInput("");
    setHeroNotice("");
    if (heroBgFileInputRef.current) {
      heroBgFileInputRef.current.value = "";
    }
  };

  const handleUseSampleBanner = () => {
    const sampleUrl = "/hero-banner-sample.jpg";
    setHeroBgPreview(sampleUrl);
    setHeroBgInput(sampleUrl);
    setHeroNotice("✓ تم اختيار صورة البانر التجريبية (المدينة الليلية). اضغط حفظ لتطبيقها.");
    if (heroBgFileInputRef.current) {
      heroBgFileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-1.5 bg-[#F8FAFC] rounded-xl p-1.5 border border-[#E2E8F0] w-fit">
        {(["colors", "services", "projects", "contact_services", "content"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-5 py-2.5 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${
              activeTab === tab
                ? "bg-white text-[#004B4B] shadow-sm border border-[#E2E8F0]"
                : "text-[#64748B] hover:text-[#1B2A4A]"
            }`}
          >
            {tab === "colors" && (
              <>
                <Palette className="w-4 h-4" /> الهوية والمظهر والألوان
              </>
            )}
            {tab === "services" && (
              <>
                <Briefcase className="w-4 h-4 text-[#004B4B]" /> تعديل قسم «خدماتنا»
              </>
            )}
            {tab === "projects" && (
              <>
                <Building2 className="w-4 h-4 text-[#004B4B]" /> تعديل نصوص «مشاريعنا»
              </>
            )}
            {tab === "contact_services" && (
              <>
                <ListOrdered className="w-4 h-4 text-[#004B4B]" /> فئات «الخدمة المطلوبة» (تواصل معنا)
              </>
            )}
            {tab === "content" && (
              <>
                <FileText className="w-4 h-4" /> باقي نصوص ومحتوى الصفحة
              </>
            )}
          </button>
        ))}
      </div>

      {/* Colors & Visual Identity Tab */}
      {activeTab === "colors" && (
        <form action={settingsAction} encType="multipart/form-data">
          
          {/* 1. Visual Identity & Media (Logo + Hero Background) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            
            {/* Logo Management */}
            <div className="bg-white rounded-xl border border-[#E2E8F0] p-5 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="w-8 h-8 rounded-lg bg-[#004B4B]/10 text-[#004B4B] flex items-center justify-center font-bold">
                      <ImageIcon className="w-4 h-4" />
                    </span>
                    <label className="text-base font-bold text-[#1B2A4A]">شعار الموقع (Logo)</label>
                  </div>
                  <button
                    type="button"
                    onClick={handleResetLogo}
                    className="text-xs text-[#64748B] hover:text-[#004B4B] flex items-center gap-1 transition-colors"
                    title="استعادة الشعار الافتراضي"
                  >
                    <RotateCcw className="w-3 h-3" /> استعادة الافتراضي
                  </button>
                </div>
                <p className="text-xs text-[#64748B] mb-4">
                  يظهر في الشريط العلوي (الهيدر) وفي أسفل الموقع (الفوتر). يمكنك رفع صورة من جهازك أو وضع رابط مباشر.
                </p>

                {/* Logo Preview Box */}
                <div className="relative rounded-xl border border-[#E2E8F0] bg-gradient-to-r from-gray-50 to-gray-100 p-6 flex items-center justify-center min-h-[110px] mb-4 overflow-hidden">
                  {logoPreview ? (
                    <img
                      src={logoPreview}
                      alt="معاينة الشعار"
                      className="max-h-16 w-auto object-contain transition-transform hover:scale-105"
                    />
                  ) : (
                    <span className="text-xs text-[#94A3B8]">لا يوجد شعار محدد</span>
                  )}
                </div>

                {/* Upload & URL Inputs */}
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-semibold text-[#475569] mb-1.5">
                      رفع شعار جديد من جهازك
                    </label>
                    <input
                      type="file"
                      name="logo_file"
                      ref={logoFileInputRef}
                      accept="image/*"
                      onChange={handleLogoFileChange}
                      className="w-full text-xs text-[#64748B] file:mr-0 file:ml-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-[#004B4B]/10 file:text-[#004B4B] hover:file:bg-[#004B4B]/20 cursor-pointer border border-[#E2E8F0] rounded-lg p-1"
                    />
                    {logoOptimizing && (
                      <p className="text-[11px] text-[#004B4B] mt-1.5 flex items-center gap-1 font-medium animate-pulse">
                        <Loader2 className="w-3 h-3 animate-spin" /> {logoNotice}
                      </p>
                    )}
                    {!logoOptimizing && logoNotice && (
                      <p className="text-[11px] text-green-700 mt-1.5 font-medium flex items-center gap-1">
                        <Check className="w-3 h-3" /> {logoNotice}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-[#475569] mb-1.5">
                      أو رابط الشعار المباشر (URL)
                    </label>
                    <input
                      type="text"
                      name="logo_url"
                      value={logoUrlInput}
                      onChange={(e) => {
                        setLogoUrlInput(e.target.value);
                        setLogoPreview(e.target.value);
                      }}
                      dir="ltr"
                      placeholder="https://... أو /logo-horizontal.png"
                      className="w-full px-3 py-2 border border-[#E2E8F0] rounded-lg text-xs text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                    />
                  </div>

                  {/* Specifications & Dimensions Guide */}
                  <div className="bg-blue-50/70 border border-blue-100 rounded-lg p-3 text-[11px] text-[#1B2A4A] space-y-1">
                    <div className="font-bold flex items-center gap-1.5 text-blue-900">
                      <Info className="w-3.5 h-3.5 text-blue-600 flex-shrink-0" />
                      المقاسات والمواصفات الموصى بها للشعار (Logo):
                    </div>
                    <div className="text-[#475569] leading-relaxed pr-5">
                      • <strong>الأبعاد:</strong> عرض 400 إلى 800 بكسل × ارتفاع 100 إلى 180 بكسل (أفقي).<br />
                      • <strong>الصيغة:</strong> PNG بخلفية شفافة (Transparent) أو SVG.<br />
                      • <strong>حجم الملف:</strong> يفضل أقل من 500 كيلوبايت.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Hero Background Banner */}
            <div className="bg-white rounded-xl border border-[#E2E8F0] p-5 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="w-8 h-8 rounded-lg bg-[#004B4B]/10 text-[#004B4B] flex items-center justify-center font-bold">
                      <Sparkles className="w-4 h-4" />
                    </span>
                    <label className="text-base font-bold text-[#1B2A4A]">صورة خلفية الواجهة (Hero Banner)</label>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={handleUseSampleBanner}
                      className="text-xs text-[#004B4B] hover:underline flex items-center gap-1 font-semibold"
                      title="استخدام صورة البانر التجريبية"
                    >
                      تجربة بانر المدينة
                    </button>
                    {heroBgPreview && (
                      <button
                        type="button"
                        onClick={handleClearHeroBg}
                        className="text-xs text-red-600 hover:text-red-700 flex items-center gap-1 transition-colors"
                        title="حذف صورة الخلفية والعودة للوضع الافتراضي"
                      >
                        <Trash2 className="w-3 h-3" /> إزالة
                      </button>
                    )}
                  </div>
                </div>
                <p className="text-xs text-[#64748B] mb-4">
                  تظهر كخلفية فخمة مع تدرج لوني في أعلى الصفحة الرئيسية. يدعم رفع الصور الكبيرة ويتم تحسينها تلقائياً.
                </p>

                {/* Hero Preview Box */}
                <div className="relative rounded-xl border border-[#E2E8F0] h-[110px] mb-4 overflow-hidden flex items-center justify-center bg-[#F9F3EC]">
                  {heroBgPreview ? (
                    <>
                      <img
                        src={heroBgPreview}
                        alt="معاينة خلفية الهيرو"
                        className="absolute inset-0 w-full h-full object-cover object-center"
                      />
                      <div className="absolute inset-0 bg-gradient-to-b from-[#004B4B]/40 to-[#004B4B]/80 flex items-center justify-center">
                        <span className="text-xs font-bold text-white bg-black/40 px-3 py-1 rounded-full backdrop-blur-sm">
                          معاينة الخلفية الفعالة
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="text-center p-3">
                      <p className="text-xs font-semibold text-[#1B2A4A]">التدرج اللوني الافتراضي نشط</p>
                      <p className="text-[11px] text-[#64748B] mt-0.5">لم يتم اختيار صورة خلفية، سيتم استخدام لون الخلفية المختار</p>
                    </div>
                  )}
                </div>

                {/* Upload & URL Inputs */}
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-semibold text-[#475569] mb-1.5">
                      رفع صورة خلفية جديدة من جهازك
                    </label>
                    <input
                      type="file"
                      name="hero_bg_file"
                      ref={heroBgFileInputRef}
                      accept="image/*"
                      onChange={handleHeroBgFileChange}
                      className="w-full text-xs text-[#64748B] file:mr-0 file:ml-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-[#004B4B]/10 file:text-[#004B4B] hover:file:bg-[#004B4B]/20 cursor-pointer border border-[#E2E8F0] rounded-lg p-1"
                    />
                    {heroOptimizing && (
                      <p className="text-[11px] text-[#004B4B] mt-1.5 flex items-center gap-1 font-medium animate-pulse">
                        <Loader2 className="w-3 h-3 animate-spin" /> {heroNotice}
                      </p>
                    )}
                    {!heroOptimizing && heroNotice && (
                      <p className="text-[11px] text-green-700 mt-1.5 font-medium flex items-center gap-1">
                        <Check className="w-3 h-3" /> {heroNotice}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-[#475569] mb-1.5">
                      أو رابط الصورة المباشر (URL)
                    </label>
                    <input
                      type="text"
                      name="hero_bg_image"
                      value={heroBgInput}
                      onChange={(e) => {
                        setHeroBgInput(e.target.value);
                        setHeroBgPreview(e.target.value);
                      }}
                      dir="ltr"
                      placeholder="https://... رابط صورة عالي الدقة"
                      className="w-full px-3 py-2 border border-[#E2E8F0] rounded-lg text-xs text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                    />
                  </div>

                  {/* Specifications & Dimensions Guide */}
                  <div className="bg-blue-50/70 border border-blue-100 rounded-lg p-3 text-[11px] text-[#1B2A4A] space-y-1">
                    <div className="font-bold flex items-center gap-1.5 text-blue-900">
                      <Info className="w-3.5 h-3.5 text-blue-600 flex-shrink-0" />
                      المقاسات والمواصفات الموصى بها لصورة الخلفية (Hero Banner):
                    </div>
                    <div className="text-[#475569] leading-relaxed pr-5">
                      • <strong>الأبعاد:</strong> 1920 × 1080 بكسل (Full HD) أو 2560 × 1440 بكسل (2K) بنسبة عرض 16:9.<br />
                      • <strong>الصيغة:</strong> JPG أو WebP (أو PNG).<br />
                      • <strong>حجم الملف:</strong> ما بين 500 كيلوبايت إلى 2 ميجابايت لأفضل سرعة تصفح.
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* 2. Site Typography Scaling (Font Size Control) */}
          <div className="bg-white rounded-xl border border-[#E2E8F0] p-5 shadow-sm mb-6">
            <div className="flex items-center gap-2 mb-2">
              <span className="w-8 h-8 rounded-lg bg-[#004B4B]/10 text-[#004B4B] flex items-center justify-center font-bold">
                <Type className="w-4 h-4" />
              </span>
              <div>
                <h3 className="text-base font-bold text-[#1B2A4A]">مقياس حجم الخط في الموقع (Site Font Scale)</h3>
                <p className="text-xs text-[#64748B]">
                  يمكنك تكبير خطوط كامل الموقع بنسب متناسقة لتحسين راحة القراءة والوضوح لزوار الموقع.
                </p>
              </div>
            </div>

            <input type="hidden" name="font_scale" value={fontScale} />

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
              {[
                { 
                  id: "normal", 
                  title: "عادي (100% - 16px)", 
                  desc: "المقاس القياسي المتناسق لجميع الشاشات",
                  sampleSize: "text-sm"
                },
                { 
                  id: "medium", 
                  title: "متوسط (108% - 17px)", 
                  desc: "تكبير متزن يعطي وضوحاً ممتازاً وسهل القراءة",
                  sampleSize: "text-base"
                },
                { 
                  id: "large", 
                  title: "كبير ومريح (115% - 18px)", 
                  desc: "أكبر مقاس، مريح جداً للعين وكبار السن",
                  sampleSize: "text-lg"
                },
              ].map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => setFontScale(opt.id)}
                  className={`text-right p-4 rounded-xl border-2 transition-all cursor-pointer relative ${
                    fontScale === opt.id
                      ? "border-[#004B4B] bg-[#004B4B]/5 shadow-sm"
                      : "border-[#E2E8F0] bg-white hover:border-[#004B4B]/40"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-sm text-[#1B2A4A]">{opt.title}</span>
                    <span className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                      fontScale === opt.id ? "border-[#004B4B] bg-[#004B4B]" : "border-[#CBD5E1]"
                    }`}>
                      {fontScale === opt.id && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
                    </span>
                  </div>
                  <p className="text-xs text-[#64748B] mb-3">{opt.desc}</p>
                  <div className="bg-white/80 p-2.5 rounded-lg border border-[#E2E8F0]/70">
                    <span className="text-[10px] text-[#94A3B8] block mb-0.5">معاينة النص:</span>
                    <p className={`font-semibold text-[#1B2A4A] truncate ${opt.sampleSize}`}>
                      دار إعمار الغربية للمقاولات العامة
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* 3. Color Pickers */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {[
              { label: "اللون الأساسي", name: "primary_color", key: "primary" as const, desc: "الهيدر، أزرار CTA، العناوين" },
              { label: "اللون الثانوي (الخلفية)", name: "secondary_color", key: "secondary" as const, desc: "خلفية الصفحة الرئيسية" },
              { label: "لون التأكيد (الرمادي)", name: "accent_color", key: "accent" as const, desc: "النصوص الثانوية والفواصل" },
            ].map(({ label, name, key, desc }) => (
              <div key={name} className="bg-white rounded-xl border border-[#E2E8F0] p-5 shadow-sm">
                <label className="block text-sm font-bold text-[#1B2A4A] mb-1">{label}</label>
                <p className="text-xs text-[#64748B] mb-4">{desc}</p>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    name={name}
                    defaultValue={
                      key === "primary" ? initialSettings.primary_color
                      : key === "secondary" ? initialSettings.secondary_color
                      : initialSettings.accent_color
                    }
                    onChange={(e) => updatePreview(key, e.target.value)}
                    className="w-14 h-14 rounded-lg cursor-pointer border-2 border-[#E2E8F0] p-1"
                  />
                  <div>
                    <p className="text-xs text-[#64748B] mb-1">كود اللون (Hex)</p>
                    <input
                      type="text"
                      value={
                        key === "primary" ? previewColors.primary
                        : key === "secondary" ? previewColors.secondary
                        : previewColors.accent
                      }
                      onChange={(e) => {
                        if (/^#[0-9A-Fa-f]{0,6}$/.test(e.target.value)) {
                          updatePreview(key, e.target.value);
                        }
                      }}
                      className="w-32 px-3 py-2 border border-[#E2E8F0] rounded-lg text-sm font-mono text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                      placeholder="#004B4B"
                    />
                  </div>
                </div>
                {/* Color swatch preview */}
                <div
                  className="mt-4 h-8 rounded-lg border border-[#E2E8F0]"
                  style={{
                    background: key === "primary" ? previewColors.primary
                      : key === "secondary" ? previewColors.secondary
                      : previewColors.accent
                  }}
                />
              </div>
            ))}
          </div>

          {/* 4. Other Settings */}
          <div className="bg-white rounded-xl border border-[#E2E8F0] p-5 shadow-sm mb-6">
            <h3 className="text-sm font-bold text-[#1B2A4A] mb-4">إعدادات عامة</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-2">اسم الشركة</label>
                <input
                  type="text"
                  name="company_name"
                  defaultValue={initialSettings.company_name}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-2">الإيميل المستقبل للطلبات</label>
                <input
                  type="email"
                  name="contact_email"
                  defaultValue={initialSettings.contact_email}
                  dir="ltr"
                  placeholder="info@daremmar.com"
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-2">تفعيل المدونة</label>
                <div className="flex items-center gap-3 mt-1">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="hidden"
                      name="is_blog_enabled"
                      value={initialSettings.is_blog_enabled ? "true" : "false"}
                    />
                    <input
                      type="checkbox"
                      id="blog-toggle"
                      defaultChecked={initialSettings.is_blog_enabled}
                      onChange={(e) => {
                        const hidden = document.querySelector<HTMLInputElement>('input[name="is_blog_enabled"]');
                        if (hidden) hidden.value = e.target.checked ? "true" : "false";
                      }}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[#E2E8F0] peer-focus:ring-2 peer-focus:ring-[#004B4B]/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#004B4B]" />
                  </label>
                  <span className="text-sm text-[#64748B]">
                    {initialSettings.is_blog_enabled ? "مفعّلة — يظهر رابط المدونة في الهيدر" : "معطّلة — المدونة مخفية"}
                  </span>
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-2">تفعيل أرقام الإنجازات (Trust Bar)</label>
                <div className="flex items-center gap-3 mt-1">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="hidden"
                      name="content_trust_enabled"
                      value={contentRows.find(r => r.key === "trust_enabled")?.value || "true"}
                    />
                    <input
                      type="checkbox"
                      defaultChecked={(contentRows.find(r => r.key === "trust_enabled")?.value || "true") === "true"}
                      onChange={(e) => {
                        const hidden = document.querySelector<HTMLInputElement>('input[name="content_trust_enabled"]');
                        if (hidden) hidden.value = e.target.checked ? "true" : "false";
                      }}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[#E2E8F0] peer-focus:ring-2 peer-focus:ring-[#004B4B]/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#004B4B]" />
                  </label>
                  <span className="text-sm text-[#64748B]">
                    يظهر قسم (أرقام الإنجازات) في الرئيسية
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 5. Account Security & Password Change */}
          <div className="bg-white rounded-xl border border-[#E2E8F0] p-5 shadow-sm mb-6">
            <div className="flex items-center gap-2 mb-2">
              <span className="w-8 h-8 rounded-lg bg-[#004B4B]/10 text-[#004B4B] flex items-center justify-center font-bold">
                <Lock className="w-4 h-4" />
              </span>
              <div>
                <h3 className="text-base font-bold text-[#1B2A4A]">أمان الحساب وتغيير كلمة مرور لوحة التحكم</h3>
                <p className="text-xs text-[#64748B]">
                  يمكنك تغيير كلمة المرور لحساب الأدمن ({initialSettings.contact_email || "admin@dar-emaar.sa"}) مباشرة من هنا في أي وقت
                </p>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-[#F1F5F9] max-w-lg space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#475569] mb-1.5">
                  كلمة المرور الجديدة
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#475569] mb-1.5">
                  تأكيد كلمة المرور الجديدة
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>

              {passwordMsg && (
                <div className={`p-3 rounded-lg text-xs flex items-center gap-2 ${
                  passwordMsg.type === "success" 
                    ? "bg-green-50 text-green-700 border border-green-200" 
                    : "bg-red-50 text-red-700 border border-red-200"
                }`}>
                  {passwordMsg.type === "success" ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                  {passwordMsg.text}
                </div>
              )}

              <button
                type="button"
                onClick={handlePasswordChange}
                disabled={passwordLoading || !newPassword}
                className="bg-[#1B2A4A] hover:bg-[#1B2A4A]/90 disabled:opacity-50 text-white px-5 py-2.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2"
              >
                {passwordLoading ? (
                  <><Loader2 className="w-3.5 h-3.5 animate-spin" /> جارٍ الحفظ...</>
                ) : (
                  <><Lock className="w-3.5 h-3.5" /> تحديث كلمة المرور</>
                )}
              </button>
            </div>
          </div>

          {/* 6. Footer Contact Info */}
          <div className="bg-white rounded-xl border border-[#E2E8F0] p-5 shadow-sm mb-6">
            <h3 className="text-sm font-bold text-[#1B2A4A] mb-4">بيانات الفوتر (أسفل الموقع) والتواصل</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-5">
              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-2">رقم الجوال</label>
                <input
                  type="text"
                  name="phone"
                  defaultValue={initialSettings.phone}
                  dir="ltr"
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] text-left focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-2">رقم الواتساب (رابط)</label>
                <input
                  type="url"
                  name="whatsapp"
                  defaultValue={initialSettings.whatsapp}
                  dir="ltr"
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] text-left focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-2">رابط الانستجرام</label>
                <input
                  type="text"
                  name="instagram"
                  defaultValue={initialSettings.instagram}
                  dir="ltr"
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] text-left focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-2">رابط تويتر / X</label>
                <input
                  type="text"
                  name="twitter"
                  defaultValue={initialSettings.twitter}
                  dir="ltr"
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] text-left focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-semibold text-[#475569] mb-2">أوقات العمل</label>
                <input
                  type="text"
                  name="working_hours"
                  defaultValue={initialSettings.working_hours}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-semibold text-[#475569] mb-2">العنوان</label>
                <input
                  type="text"
                  name="address"
                  defaultValue={initialSettings.address}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-semibold text-[#475569] mb-2">الوصف التعريفي (تحت الشعار في الفوتر)</label>
                <textarea
                  name="footer_description"
                  defaultValue={initialSettings.footer_description}
                  rows={2}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] resize-none focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>
            </div>
          </div>

          {/* Status + Submit */}
          {settingsState.error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm mb-4 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" /> {settingsState.error}
            </div>
          )}
          {settingsState.success && (
            <div className="bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 text-sm mb-4 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> تم حفظ الإعدادات والشعار والخلفية بنجاح. سيتم تطبيق التغييرات فوراً.
            </div>
          )}
          <button
            type="submit"
            disabled={settingsPending || heroOptimizing || logoOptimizing}
            className="bg-[#004B4B] hover:bg-[#004B4B]/90 disabled:opacity-60 text-white px-8 py-3 rounded-xl text-sm font-bold transition-all shadow-lg shadow-[#004B4B]/20"
          >
            {settingsPending ? "جارٍ الحفظ والرفع..." : <span className="flex items-center gap-2 justify-center"><Save className="w-4 h-4" /> حفظ كل الإعدادات</span>}
          </button>
        </form>
      )}

      {/* Services Tab */}
      {activeTab === "services" && (
        <form action={contentAction} className="space-y-6">
          {/* Section 1: Services Header & Main Headline */}
          <div className="bg-white rounded-xl border border-[#E2E8F0] p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-[#F1F5F9]">
              <span className="w-8 h-8 rounded-lg bg-[#004B4B]/10 text-[#004B4B] flex items-center justify-center font-bold">
                <Briefcase className="w-4 h-4" />
              </span>
              <div>
                <h3 className="text-base font-bold text-[#1B2A4A]">العناوين الرئيسية لقسم خدماتنا (الهيد لاين والوصف)</h3>
                <p className="text-xs text-[#64748B]">تظهر في أعلى قسم الخدمات بالصفحة الرئيسية للموقع</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-2">
                  الشارة العلوية (Badge)
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(services_badge)</span>
                </label>
                <input
                  type="text"
                  name="content_services_badge"
                  defaultValue={contentRows.find(r => r.key === "services_badge")?.value || "خدماتنا"}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-2">
                  العنوان الرئيسي (هيد لاين قسم الخدمات)
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(services_title)</span>
                </label>
                <input
                  type="text"
                  name="content_services_title"
                  defaultValue={contentRows.find(r => r.key === "services_title")?.value || "ماذا نقدم لك؟"}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20 font-bold"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-sm font-semibold text-[#475569] mb-2">
                  الوصف التمهيدي لقسم الخدمات
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(services_subtitle)</span>
                </label>
                <textarea
                  name="content_services_subtitle"
                  defaultValue={contentRows.find(r => r.key === "services_subtitle")?.value || "نقدم مجموعة متكاملة من الخدمات الإنشائية تحت سقف واحد — لضمان تجربة بناء سلسة وبلا تعقيد"}
                  rows={2}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] resize-none focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>
            </div>
          </div>

          {/* Section 2: Individual Service Cards (3 Services) */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {[
              { 
                num: 1, 
                titleKey: "service_1_title", 
                descKey: "service_1_desc", 
                highlightsKey: "service_1_highlights", 
                defaultTitle: "التصميم والبناء", 
                defaultDesc: "تصميم معماري متكامل مع هندسة متخصصة وتنفيذ بجودة عالية وتكلفة تنافسية، من رسم المخططات حتى استلام المفتاح.", 
                defaultHighlights: "تصميم معماري احترافي\nإشراف هندسي متكامل\nمواد بناء عالية الجودة" 
              },
              { 
                num: 2, 
                titleKey: "service_2_title", 
                descKey: "service_2_desc", 
                highlightsKey: "service_2_highlights", 
                defaultTitle: "التشطيبات الداخلية", 
                defaultDesc: "تشطيبات فاخرة تناسب ذوقك وميزانيتك — من الجبس والدهانات حتى الأرضيات والأسقف المعلقة بأعلى المعايير.", 
                defaultHighlights: "أسقف جبسية وديكور\nدهانات وورق جدران\nأرضيات وبلاط فاخر" 
              },
              { 
                num: 3, 
                titleKey: "service_3_title", 
                descKey: "service_3_desc", 
                highlightsKey: "service_3_highlights", 
                defaultTitle: "إدارة المشاريع", 
                defaultDesc: "إدارة احترافية كاملة للمشاريع من التخطيط والجدولة الزمنية حتى التسليم النهائي مع ضمان الالتزام بالموعد والميزانية.", 
                defaultHighlights: "جدولة زمنية دقيقة\nتقارير دورية شاملة\nتنسيق كامل مع المقاولين" 
              },
            ].map(({ num, titleKey, descKey, highlightsKey, defaultTitle, defaultDesc, defaultHighlights }) => (
              <div key={num} className="bg-white rounded-xl border border-[#E2E8F0] p-5 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-4 pb-2 border-b border-[#F1F5F9]">
                    <span className="w-6 h-6 rounded-full bg-[#004B4B] text-white text-xs font-bold flex items-center justify-center">
                      {num}
                    </span>
                    <h4 className="text-sm font-bold text-[#1B2A4A]">بطاقة الخدمة رقم ({num})</h4>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-xs font-semibold text-[#475569] mb-1.5">
                        اسم / عنوان الخدمة
                      </label>
                      <input
                        type="text"
                        name={`content_${titleKey}`}
                        defaultValue={contentRows.find(r => r.key === titleKey)?.value || defaultTitle}
                        className="w-full px-3 py-2 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] font-bold focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-[#475569] mb-1.5">
                        وصف الخدمة
                      </label>
                      <textarea
                        name={`content_${descKey}`}
                        defaultValue={contentRows.find(r => r.key === descKey)?.value || defaultDesc}
                        rows={3}
                        className="w-full px-3 py-2 border border-[#E2E8F0] rounded-lg text-xs text-[#1B2A4A] resize-none focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20 leading-relaxed"
                      />
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-1.5">
                        <label className="block text-xs font-semibold text-[#475569]">
                          خانات ومميزات الخدمة (Highlights)
                        </label>
                        <span className="text-[10px] text-[#94A3B8]">سطر لكل ميزة</span>
                      </div>
                      <textarea
                        name={`content_${highlightsKey}`}
                        defaultValue={contentRows.find(r => r.key === highlightsKey)?.value || defaultHighlights}
                        rows={4}
                        placeholder={"ميزة 1\nميزة 2\nميزة 3"}
                        className="w-full px-3 py-2 border border-[#E2E8F0] rounded-lg text-xs text-[#1B2A4A] resize-none focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20 leading-relaxed font-mono"
                      />
                      <p className="text-[10px] text-[#64748B] mt-1">
                        * تظهر كنقاط مرتبة في بطاقة الخدمة. افصل بين كل ميزة بسطر جديد (Enter).
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Section 3: Footer note of services */}
          <div className="bg-white rounded-xl border border-[#E2E8F0] p-6 shadow-sm">
            <h4 className="text-sm font-bold text-[#1B2A4A] mb-3 pb-2 border-b border-[#F1F5F9]">
              النص التوضيحي وروابط التواصل أسفل كروت الخدمات
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div>
                <label className="block text-xs font-semibold text-[#475569] mb-1.5">
                  النص التوضيحي (الخدمات الإضافية)
                </label>
                <textarea
                  name="content_services_footer_text"
                  defaultValue={contentRows.find(r => r.key === "services_footer_text")?.value || "نقدم أيضاً: أعمال الحفر والردم، البنية التحتية، الطاقة المتجددة، خدمات لوجستية، وأكثر من 10 خدمات متخصصة أخرى."}
                  rows={2}
                  className="w-full px-3 py-2 border border-[#E2E8F0] rounded-lg text-xs text-[#1B2A4A] resize-none focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#475569] mb-1.5">
                  نص رابط التواصل
                </label>
                <input
                  type="text"
                  name="content_services_footer_cta"
                  defaultValue={contentRows.find(r => r.key === "services_footer_cta")?.value || "تواصل معنا لمعرفة كل خدماتنا ←"}
                  className="w-full px-3 py-2 border border-[#E2E8F0] rounded-lg text-xs text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20 font-semibold"
                />
              </div>
            </div>
          </div>

          {/* Status + Submit */}
          {contentState.error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4" /> {contentState.error}
            </div>
          )}
          {contentState.success && (
            <div className="bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> تم حفظ نصوص ومحتوى الخدمات بنجاح. سيتم تحديث الموقع فوراً.
            </div>
          )}

          <button
            type="submit"
            disabled={contentPending}
            className="bg-[#004B4B] hover:bg-[#004B4B]/90 disabled:opacity-60 text-white px-8 py-3 rounded-xl text-sm font-bold transition-all shadow-lg shadow-[#004B4B]/20 flex items-center gap-2"
          >
            {contentPending ? "جارٍ الحفظ..." : <><Save className="w-4 h-4" /> حفظ كل نصوص قسم خدماتنا</>}
          </button>
        </form>
      )}

      {/* Projects Tab */}
      {activeTab === "projects" && (
        <form action={contentAction} className="space-y-6">
          {/* Section 1: Landing Page Projects Section */}
          <div className="bg-white rounded-xl border border-[#E2E8F0] p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-[#F1F5F9]">
              <span className="w-8 h-8 rounded-lg bg-[#004B4B]/10 text-[#004B4B] flex items-center justify-center font-bold">
                <Building2 className="w-4 h-4" />
              </span>
              <div>
                <h3 className="text-base font-bold text-[#1B2A4A]">نصوص قسم المشاريع بالصفحة الرئيسية</h3>
                <p className="text-xs text-[#64748B]">القسم الموجود في الصفحة الرئيسية (الهيد لاين، الوصف، شارة البادج، والأزرار)</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  شارة قسم المشاريع (Badge)
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_badge)</span>
                </label>
                <input
                  type="text"
                  name="content_projects_badge"
                  defaultValue={contentRows.find(r => r.key === "projects_badge")?.value || "مشاريعنا"}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20 font-bold"
                />
                <p className="text-[11px] text-[#004B4B] mt-1 font-medium">
                  * تم تحسينها لتظهر في أعلى القسم كشارة مضيئة وواضحة وبارزة بلون زمردي جذاب.
                </p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  العنوان الرئيسي (هيد لاين قسم المشاريع)
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_title)</span>
                </label>
                <input
                  type="text"
                  name="content_projects_title"
                  defaultValue={contentRows.find(r => r.key === "projects_title")?.value || "مشاريع نفخر بتنفيذها"}
                  placeholder="مشاريع نفخر بتنفيذها"
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20 font-bold"
                />
                <p className="text-[11px] text-[#64748B] mt-1">
                  * تم تعديلها افتراضياً إلى: "مشاريع نفخر بتنفيذها" ويمكنك تعديلها في أي وقت.
                </p>
              </div>

              <div className="sm:col-span-2">
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  الوصف التمهيدي لقسم المشاريع
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_subtitle)</span>
                </label>
                <textarea
                  name="content_projects_subtitle"
                  defaultValue={contentRows.find(r => r.key === "projects_subtitle")?.value || "نفخر بتسليم مشاريع تتجاوز توقعات عملائنا في الجودة والالتزام بالمواعيد"}
                  rows={2}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] resize-none focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  شارة المشروع المميز
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_featured_label)</span>
                </label>
                <input
                  type="text"
                  name="content_projects_featured_label"
                  defaultValue={contentRows.find(r => r.key === "projects_featured_label")?.value || "مشروع مميز"}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  نص زر اتخاذ الإجراء في كارت المشروع المميز
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_featured_cta)</span>
                </label>
                <input
                  type="text"
                  name="content_projects_featured_cta"
                  defaultValue={contentRows.find(r => r.key === "projects_featured_cta")?.value || "أريد مشروعاً مشابهاً"}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20 font-semibold"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  نص زر تصفح كل المشاريع (أسفل شبكة المشاريع)
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_view_all_cta)</span>
                </label>
                <input
                  type="text"
                  name="content_projects_view_all_cta"
                  defaultValue={contentRows.find(r => r.key === "projects_view_all_cta")?.value || "عرض جميع المشاريع"}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20 font-semibold"
                />
              </div>
            </div>
          </div>

          {/* Section 2: Standalone /projects Page Texts */}
          <div className="bg-white rounded-xl border border-[#E2E8F0] p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-[#F1F5F9]">
              <span className="w-8 h-8 rounded-lg bg-[#004B4B]/10 text-[#004B4B] flex items-center justify-center font-bold">
                <Layers className="w-4 h-4" />
              </span>
              <div>
                <h3 className="text-base font-bold text-[#1B2A4A]">نصوص صفحة المشاريع المستقلة (/projects)</h3>
                <p className="text-xs text-[#64748B]">تظهر في الصفحة المخصصة لمعرض المشاريع الكامل</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  شارة رأس صفحة المشاريع
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_page_badge)</span>
                </label>
                <input
                  type="text"
                  name="content_projects_page_badge"
                  defaultValue={contentRows.find(r => r.key === "projects_page_badge")?.value || "معرض الأعمال"}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  العنوان الرئيسي لصفحة المشاريع
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_page_title)</span>
                </label>
                <input
                  type="text"
                  name="content_projects_page_title"
                  defaultValue={contentRows.find(r => r.key === "projects_page_title")?.value || "مشاريعنا"}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20 font-bold"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  الوصف التمهيدي لصفحة المشاريع
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_page_subtitle)</span>
                </label>
                <textarea
                  name="content_projects_page_subtitle"
                  defaultValue={contentRows.find(r => r.key === "projects_page_subtitle")?.value || "أكثر من 200 مشروع منجز عبر مختلف القطاعات — تصفح أبرز إنجازاتنا"}
                  rows={2}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] resize-none focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  عنوان صندوق التواصل في أسفل صفحة المشاريع
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_page_cta_title)</span>
                </label>
                <input
                  type="text"
                  name="content_projects_page_cta_title"
                  defaultValue={contentRows.find(r => r.key === "projects_page_cta_title")?.value || "هل لديك مشروع مماثل؟"}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20 font-bold"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  نص زر التواصل في أسفل صفحة المشاريع
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_page_cta_button)</span>
                </label>
                <input
                  type="text"
                  name="content_projects_page_cta_button"
                  defaultValue={contentRows.find(r => r.key === "projects_page_cta_button")?.value || "طلب استشارة مجانية"}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20 font-semibold"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-sm font-semibold text-[#475569] mb-1.5">
                  وصف صندوق التواصل في أسفل صفحة المشاريع
                  <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">(projects_page_cta_desc)</span>
                </label>
                <input
                  type="text"
                  name="content_projects_page_cta_desc"
                  defaultValue={contentRows.find(r => r.key === "projects_page_cta_desc")?.value || "احصل على استشارة مجانية من فريق خبرائنا"}
                  className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                />
              </div>
            </div>
          </div>

          {/* Status + Submit */}
          {contentState.error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4" /> {contentState.error}
            </div>
          )}
          {contentState.success && (
            <div className="bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> تم حفظ نصوص ومحتوى قسم المشاريع بنجاح. سيتم تحديث الموقع فوراً.
            </div>
          )}

          <button
            type="submit"
            disabled={contentPending}
            className="bg-[#004B4B] hover:bg-[#004B4B]/90 disabled:opacity-60 text-white px-8 py-3 rounded-xl text-sm font-bold transition-all shadow-lg shadow-[#004B4B]/20 flex items-center gap-2"
          >
            {contentPending ? "جارٍ الحفظ..." : <><Save className="w-4 h-4" /> حفظ كل نصوص قسم وصفحة المشاريع</>}
          </button>
        </form>
      )}

      {/* Contact Services Tab */}
      {activeTab === "contact_services" && (
        <form action={contentAction} className="space-y-6">
          <input
            type="hidden"
            name="content_contact_services_list"
            value={JSON.stringify(contactServices.map((s) => s.trim()).filter(Boolean))}
          />

          {/* Intro Card */}
          <div className="bg-white rounded-xl border border-[#E2E8F0] p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 mb-5 border-b border-[#F1F5F9]">
              <div className="flex items-center gap-3">
                <span className="w-10 h-10 rounded-xl bg-[#004B4B]/10 text-[#004B4B] flex items-center justify-center font-bold">
                  <ListOrdered className="w-5 h-5" />
                </span>
                <div>
                  <h3 className="text-lg font-bold text-[#1B2A4A]">
                    إدارة فئات «الخدمة المطلوبة» (تواصل معنا)
                  </h3>
                  <p className="text-xs text-[#64748B] mt-0.5">
                    الخيارات التي تظهر للزائر في القائمة المنسدلة عند طلب تسعيرة أو استشارة في نموذج تواصل معنا
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span
                  className={`px-3 py-1.5 rounded-full text-xs font-bold border ${
                    contactServices.length >= 6
                      ? "bg-amber-50 text-amber-700 border-amber-200"
                      : "bg-[#004B4B]/10 text-[#004B4B] border-[#004B4B]/20"
                  }`}
                >
                  العدد المعتمد: {contactServices.length} من 6 خانات
                </span>
                <button
                  type="button"
                  onClick={handleResetServices}
                  className="text-xs text-[#64748B] hover:text-[#004B4B] px-2.5 py-1.5 rounded-lg border border-[#E2E8F0] hover:border-[#004B4B]/30 transition-colors flex items-center gap-1 font-semibold"
                  title="استعادة الـ 5 خدمات الافتراضية"
                >
                  <RotateCcw className="w-3 h-3" /> استعادة الافتراضي
                </button>
              </div>
            </div>

            {/* Instruction Notice */}
            <div className="bg-blue-50/70 border border-blue-100 rounded-xl p-4 text-xs text-[#1B2A4A] mb-6 flex items-start gap-3">
              <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="font-bold text-blue-900">
                  قواعد التحكم بخانات الخدمات (من 1 إلى 6 خانات كحد أقصى):
                </p>
                <div className="text-[#475569] leading-relaxed">
                  • يمكنك تعديل مسمى أي خدمة مباشرة داخل الخانة الخاصة بها.<br />
                  • يمكنك إضافة خانات جديدة حتى تصل إلى <strong>6 خانات كحد أقصى</strong> لتناسب كافة أنشطة الشركة وتوسعاتها المستقبلية.<br />
                  • يمكنك حذف أي خانة بضغطة زر، ويجب الإبقاء على خانة واحدة على الأقل.
                </div>
              </div>
            </div>

            {/* Services Slots List */}
            <div className="space-y-3">
              {contactServices.map((serviceName, index) => (
                <div
                  key={index}
                  className="group flex flex-col sm:flex-row items-stretch sm:items-center gap-3 p-3.5 bg-[#F8FAFC] hover:bg-white border border-[#E2E8F0] hover:border-[#004B4B]/30 rounded-xl transition-all shadow-sm"
                >
                  {/* Slot Number Badge */}
                  <div className="flex items-center gap-2 sm:w-28 flex-shrink-0">
                    <span className="w-7 h-7 rounded-lg bg-[#004B4B] text-white text-xs font-bold flex items-center justify-center shadow-sm">
                      {index + 1}
                    </span>
                    <span className="text-xs font-bold text-[#475569]">
                      الخانة {index + 1}
                    </span>
                  </div>

                  {/* Input field */}
                  <div className="flex-1">
                    <input
                      type="text"
                      value={serviceName}
                      onChange={(e) => handleServiceChange(index, e.target.value)}
                      placeholder={`اكتب مسمى الخدمة رقم (${index + 1}) هنا...`}
                      className="w-full px-4 py-2.5 bg-white border border-[#CBD5E1] rounded-lg text-sm text-[#1B2A4A] font-semibold focus:outline-none focus:ring-2 focus:ring-[#004B4B]/25 focus:border-[#004B4B] transition-all"
                    />
                  </div>

                  {/* Delete Button */}
                  <div className="flex items-center justify-end sm:justify-center">
                    <button
                      type="button"
                      onClick={() => handleRemoveService(index)}
                      disabled={contactServices.length <= 1}
                      className="p-2.5 rounded-lg border border-red-200 bg-red-50/50 text-red-600 hover:bg-red-100/80 hover:text-red-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center gap-1.5 text-xs font-bold"
                      title={contactServices.length <= 1 ? "لا يمكن الحذف (يجب الإبقاء على خدمة واحدة على الأقل)" : "حذف هذه الخدمة"}
                    >
                      <Trash2 className="w-4 h-4" />
                      <span className="sm:hidden">حذف الخانة</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Add Service Button & Limit Warning */}
            <div className="mt-5 flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-[#F1F5F9]">
              {contactServices.length < 6 ? (
                <button
                  type="button"
                  onClick={handleAddService}
                  className="w-full sm:w-auto px-5 py-2.5 rounded-xl border-2 border-dashed border-[#004B4B]/40 hover:border-[#004B4B] bg-[#004B4B]/5 hover:bg-[#004B4B]/10 text-[#004B4B] text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer"
                >
                  <Plus className="w-4 h-4" />
                  إضافة خانة خدمة جديدة (متبقي {6 - contactServices.length} خدمات أخرى)
                </button>
              ) : (
                <div className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs font-bold flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-amber-600 flex-shrink-0" />
                  تم الوصول للحد الأقصى المسموح به (6 خانات). لحذف أو استبدال خدمة، قم بحذف إحداها أولاً.
                </div>
              )}

              <span className="text-xs text-[#94A3B8]">
                {contactServices.filter((s) => s.trim().length > 0).length} خدمة معتمدة ستظهر في القائمة
              </span>
            </div>
          </div>

          {/* Live Preview Card */}
          <div className="bg-white rounded-xl border border-[#E2E8F0] p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[#F1F5F9]">
              <span className="w-6 h-6 rounded-md bg-emerald-50 text-emerald-700 flex items-center justify-center text-xs font-bold">
                👁️
              </span>
              <h4 className="text-sm font-bold text-[#1B2A4A]">
                معاينة حية لشكل القائمة المنسدلة في الموقع (Live Preview)
              </h4>
            </div>
            <p className="text-xs text-[#64748B] mb-4">
              هكذا ستظهر الخيارات للعميل تماماً في نموذج التواصل بالصفحة الرئيسية:
            </p>

            <div className="max-w-md bg-[#F8FAFC] p-4 rounded-xl border border-[#E2E8F0]">
              <label className="block text-xs font-bold text-[#1B2A4A] mb-2">
                الخدمة المطلوبة
              </label>
              <select
                className="w-full px-4 py-3 bg-white border border-[#CBD5E1] rounded-lg text-sm text-[#1B2A4A] font-semibold cursor-pointer shadow-sm focus:outline-none"
                defaultValue=""
              >
                <option value="" disabled>اختر الخدمة المناسبة لك</option>
                {contactServices.map((s, idx) => (
                  <option key={idx} value={s}>
                    {s.trim() ? s : `(الخانة رقم ${idx + 1} - بانتظار كتابة المسمى)`}
                  </option>
                ))}
              </select>
              <p className="text-[11px] text-[#94A3B8] mt-2">
                * عند اختيار العميل لأي خدمة وإرسال النموذج، ستصلك في لوحة التحكم (الطلبات) والإيميل بمسمى الخدمة المختار فوراً.
              </p>
            </div>
          </div>

          {/* Status Alerts */}
          {contentState.error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4" /> {contentState.error}
            </div>
          )}
          {contentState.success && (
            <div className="bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> تم حفظ وتحديث فئات الخدمة المطلوبة بنجاح. سيتم تحديث نموذج التواصل في الموقع فوراً.
            </div>
          )}

          {/* Save Button */}
          <button
            type="submit"
            disabled={contentPending}
            className="bg-[#004B4B] hover:bg-[#004B4B]/90 disabled:opacity-60 text-white px-8 py-3 rounded-xl text-sm font-bold transition-all shadow-lg shadow-[#004B4B]/20 flex items-center gap-2"
          >
            {contentPending ? "جارٍ الحفظ..." : <><Save className="w-4 h-4" /> حفظ فئات الخدمة المطلوبة</>}
          </button>
        </form>
      )}

      {/* General Content Tab */}
      {activeTab === "content" && (
        <form action={contentAction}>
          <div className="space-y-6">
            {Object.entries(grouped)
              .filter(([section]) => section !== "services" && section !== "projects" && section !== "contact_services")
              .map(([section, rows]) => (
              <div key={section} className="bg-white rounded-xl border border-[#E2E8F0] p-6 shadow-sm">
                <h3 className="text-sm font-bold text-[#1B2A4A] mb-5 pb-3 border-b border-[#F1F5F9]">
                  {sectionLabels[section] || section}
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  {rows.map((row) => (
                    <div key={row.key} className={row.value.length > 80 ? "sm:col-span-2" : ""}>
                      <label className="block text-sm font-semibold text-[#475569] mb-2">
                        {row.label}
                        <span className="text-xs text-[#94A3B8] font-normal ms-2 font-mono">({row.key})</span>
                      </label>
                      {row.value.length > 80 ? (
                        <textarea
                          name={`content_${row.key}`}
                          defaultValue={row.value}
                          rows={3}
                          className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] resize-none focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                        />
                      ) : (
                        <input
                          type="text"
                          name={`content_${row.key}`}
                          defaultValue={row.value}
                          className="w-full px-4 py-2.5 border border-[#E2E8F0] rounded-lg text-sm text-[#1B2A4A] focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
                        />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {contentState.error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm mt-4 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" /> {contentState.error}
            </div>
          )}
          {contentState.success && (
            <div className="bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 text-sm mt-4 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> تم حفظ المحتوى بنجاح. سيتم تحديث الموقع خلال دقيقة.
            </div>
          )}
          <button
            type="submit"
            disabled={contentPending}
            className="mt-5 bg-[#004B4B] hover:bg-[#004B4B]/90 disabled:opacity-60 text-white px-8 py-3 rounded-xl text-sm font-bold transition-all shadow-lg shadow-[#004B4B]/20"
          >
            {contentPending ? "جارٍ الحفظ..." : <span className="flex items-center gap-2 justify-center"><Save className="w-4 h-4" /> حفظ المحتوى</span>}
          </button>
        </form>
      )}
    </div>
  );
}
