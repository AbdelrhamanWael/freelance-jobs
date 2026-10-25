"use client";

import { useState, useRef } from "react";
import { saveProject } from "@/app/actions/projects";
import { useRouter } from "next/navigation";
import { Upload, Image as ImageIcon, FileText, Trash2, X, AlertCircle } from "lucide-react";

interface Props {
  project?: any;
  categories: any[];
}

export default function ProjectForm({ project, categories }: Props) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [title, setTitle] = useState(project?.title || "");
  const [slug, setSlug] = useState(project?.slug || "");
  const [slugTouched, setSlugTouched] = useState(!!project?.slug);

  // Images state
  const initialImages: string[] = Array.isArray(project?.images)
    ? project.images.filter((s: string) => s && !s.startsWith("file:"))
    : [];
  const [existingImages, setExistingImages] = useState<string[]>(initialImages);
  const [imagePreviewUrls, setImagePreviewUrls] = useState<string[]>([]);
  const imageInputRef = useRef<HTMLInputElement>(null);

  // Attachment state
  const initialAttachment = project?.attachment_file && !project.attachment_file.startsWith("file:")
    ? project.attachment_file
    : "";
  const [currentAttachment, setCurrentAttachment] = useState<string>(initialAttachment);
  const [attachmentFileName, setAttachmentFileName] = useState<string>("");
  const attachmentInputRef = useRef<HTMLInputElement>(null);

  function generateSlug(text: string) {
    return text
      .toString()
      .trim()
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^\w\-أ-ي]/g, '')
      .replace(/\-\-+/g, '-')
      .replace(/^-+/, '')
      .replace(/-+$/, '');
  }

  function handleTitleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const newTitle = e.target.value;
    setTitle(newTitle);
    if (!slugTouched) {
      setSlug(generateSlug(newTitle));
    }
  }

  function handleSlugChange(e: React.ChangeEvent<HTMLInputElement>) {
    setSlug(e.target.value);
    setSlugTouched(true);
  }

  function handleImageFilesSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const urls: string[] = [];
    for (let i = 0; i < files.length; i++) {
      urls.push(URL.createObjectURL(files[i]));
    }
    setImagePreviewUrls(urls);
  }

  function handleRemoveExistingImage(index: number) {
    setExistingImages((prev) => prev.filter((_, i) => i !== index));
  }

  function handleAttachmentSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      setAttachmentFileName(file.name);
    } else {
      setAttachmentFileName("");
    }
  }

  function handleRemoveAttachment() {
    setCurrentAttachment("");
    setAttachmentFileName("");
    if (attachmentInputRef.current) {
      attachmentInputRef.current.value = "";
    }
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const formData = new FormData(e.currentTarget);
    const result = await saveProject(formData);

    if (result?.error) {
      setError(result.error);
      setLoading(false);
    } else {
      router.push("/dashboard/projects");
      router.refresh();
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-xl text-sm border border-red-200 flex items-center gap-2 font-medium">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {project?.id && <input type="hidden" name="id" value={project.id} />}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">عنوان المشروع *</label>
          <input
            name="title"
            value={title}
            onChange={handleTitleChange}
            required
            placeholder="مثال: عمارة سكنية في حي السلامة"
            className="form-input-light"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">الرابط المختصر (Slug) *</label>
          <input
            name="slug"
            value={slug}
            onChange={handleSlugChange}
            required
            className="form-input-light text-left"
            dir="auto"
            placeholder="omara-sakaniya أو عمارة-سكنية"
          />
          <p className="text-xs text-gray-500 mt-1">
            الرابط التعريفي للمشروع. يدعم الحروف الإنجليزية أو العربية، مثال: <span dir="ltr">residential-building</span> أو <span dir="rtl">عمارة-سكنية</span>
          </p>
        </div>
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">الفئة *</label>
          <select 
            name="category_id" 
            defaultValue={project?.category_id || ""} 
            required 
            className="form-input-light bg-white"
          >
            <option value="" disabled>اختر الفئة...</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">الموقع</label>
          <input name="location" defaultValue={project?.location} placeholder="مثال: جدة — حي السلامة" className="form-input-light" />
        </div>
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">العميل</label>
          <input name="client" defaultValue={project?.client} placeholder="مثال: سكن خاص" className="form-input-light" />
        </div>
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">سنة الإنجاز</label>
          <input name="year" defaultValue={project?.year} placeholder="2025" className="form-input-light" />
        </div>
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">المساحة</label>
          <input name="area" defaultValue={project?.area} placeholder="مثال: 660 م²" className="form-input-light" />
        </div>
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">المدة الزمنية</label>
          <input name="duration" defaultValue={project?.duration} placeholder="مثال: 6 أشهر" className="form-input-light" />
        </div>
      </div>

      <div>
        <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">الوصف</label>
        <textarea
          name="description"
          defaultValue={project?.description}
          rows={3}
          className="form-input-light min-h-[100px]"
          placeholder="اكتب نبذة شاملة عن المشروع والمواصفات..."
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">نطاق العمل (سطر لكل عنصر)</label>
        <textarea
          name="scope"
          defaultValue={project?.scope?.join("\n")}
          rows={4}
          className="form-input-light min-h-[120px]"
          placeholder={"أعمال الحفر والإحلال\nالهيكل الإنشائي\nأعمال العزل\nأعمال المباني والتشطيبات"}
        />
      </div>

      {/* ── Project Images Section ── */}
      <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <label className="block text-sm font-bold text-[#1B2A4A]">معرض صور المشروع (Project Gallery)</label>
            <p className="text-xs text-[#64748B] mt-0.5">
              يمكنك رفع <strong>عدة صور للمشروع</strong> معاً. الصورة الأولى تكون هي <strong>الغلاف الرئيسي</strong>، وباقي الصور تُعرض في ألبوم المشروع.
            </p>
          </div>
          <button
            type="button"
            onClick={() => imageInputRef.current?.click()}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-[#004B4B] hover:bg-[#003838] text-white rounded-lg text-xs font-bold transition-colors cursor-pointer w-fit shadow-xs"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>+ إضافة / رفع صور من جهازك</span>
          </button>
        </div>

        {/* Hidden File Input (multiple images) */}
        <input
          type="file"
          ref={imageInputRef}
          name="image_files"
          accept="image/*"
          multiple
          onChange={handleImageFilesSelected}
          className="hidden"
        />

        {/* Hidden Existing Images Input for Server Action */}
        <input
          type="hidden"
          name="images"
          value={existingImages.join(", ")}
        />

        {/* Existing Images Thumbnails */}
        {existingImages.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="block text-xs font-semibold text-[#475569]">
                الصور المحفوظة للمشروع ({existingImages.length} صور):
              </span>
              <span className="text-[11px] text-[#64748B]">الصورة الأولى على اليمين هي الغلاف الرئيسي</span>
            </div>
            <div className="flex flex-wrap gap-3">
              {existingImages.map((url, idx) => (
                <div key={idx} className={`relative group w-24 h-24 rounded-lg overflow-hidden border-2 bg-white shadow-xs ${idx === 0 ? "border-[#004B4B] ring-2 ring-[#004B4B]/20" : "border-[#E2E8F0]"}`}>
                  <img src={url} alt={`صورة ${idx + 1}`} className="w-full h-full object-cover" />
                  
                  {/* Badge for cover image vs additional */}
                  <span className={`absolute bottom-0 inset-x-0 text-[10px] text-center font-bold py-0.5 ${idx === 0 ? "bg-[#004B4B] text-white" : "bg-black/60 text-white"}`}>
                    {idx === 0 ? "الغلاف الرئيسي" : `صورة ${idx + 1}`}
                  </span>

                  <button
                    type="button"
                    onClick={() => handleRemoveExistingImage(idx)}
                    className="absolute top-1 end-1 bg-red-600 text-white rounded-md p-1 opacity-90 hover:opacity-100 transition-opacity shadow-sm"
                    title="حذف هذه الصورة"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Newly Selected Preview Thumbnails */}
        {imagePreviewUrls.length > 0 && (
          <div>
            <span className="block text-xs font-semibold text-[#004B4B] mb-2">
              ✓ تم اختيار ({imagePreviewUrls.length}) صور جديدة للرفع:
            </span>
            <div className="flex flex-wrap gap-3">
              {imagePreviewUrls.map((url, idx) => (
                <div key={idx} className="relative w-24 h-24 rounded-lg overflow-hidden border-2 border-emerald-400 bg-white shadow-xs">
                  <img src={url} alt={`جديدة ${idx + 1}`} className="w-full h-full object-cover" />
                  <span className="absolute bottom-1 start-1 bg-emerald-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded">
                    جديدة
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {existingImages.length === 0 && imagePreviewUrls.length === 0 && (
          <div className="border border-dashed border-[#CBD5E1] rounded-lg p-6 text-center text-xs text-[#94A3B8]">
            <ImageIcon className="w-8 h-8 mx-auto mb-2 text-[#CBD5E1]" />
            لم يتم إضافة صور لهذا المشروع بعد. اضغط على «اختر صوراً من جهازك» لإضافة صور المعرض.
          </div>
        )}
      </div>

      {/* ── File Attachment Section ── */}
      <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl p-5 space-y-4">
        <div>
          <label className="block text-sm font-bold text-[#1B2A4A]">ملف المشروع المرفق (PDF أو بروفايل)</label>
          <p className="text-xs text-[#64748B]">يمكنك رفع ملف PDF من جهازك أو وضع رابط تحميل مباشر للملف.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-[#475569] mb-1.5">رفع ملف جديد من جهازك</label>
            <div className="flex items-center gap-3">
              <input
                type="file"
                ref={attachmentInputRef}
                name="attachment_upload"
                accept=".pdf,.doc,.docx"
                onChange={handleAttachmentSelected}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => attachmentInputRef.current?.click()}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-[#CBD5E1] hover:border-[#004B4B] text-[#1B2A4A] rounded-lg text-xs font-bold transition-colors cursor-pointer shadow-xs"
              >
                <FileText className="w-4 h-4 text-[#004B4B]" />
                <span>{attachmentFileName || "اختيار ملف (PDF / مستند)..."}</span>
              </button>
              {(attachmentFileName || currentAttachment) && (
                <button
                  type="button"
                  onClick={handleRemoveAttachment}
                  className="text-xs text-red-600 hover:underline font-semibold"
                >
                  إزالة الملف
                </button>
              )}
            </div>

            {currentAttachment && !attachmentFileName && (
              <p className="text-[11px] text-emerald-700 mt-1.5 font-medium flex items-center gap-1">
                ✓ يوجد ملف مرفق محفوظ مسبقاً.
              </p>
            )}
            <input type="hidden" name="attachment_file" value={currentAttachment} />
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#475569] mb-1.5">اسم الملف المرفق (يظهر للزائر على الزر)</label>
            <input
              name="attachment_label"
              defaultValue={project?.attachment_label}
              className="form-input-light"
              placeholder="مثال: بروفايل المشروع، كتالوج التشطيبات"
            />
          </div>
        </div>
      </div>

      <div className="flex gap-6">
        <label className="flex items-center gap-2 text-sm font-semibold text-[#1B2A4A] cursor-pointer">
          <input
            type="checkbox"
            name="is_featured"
            value="true"
            defaultChecked={project?.is_featured}
            className="w-4 h-4 text-[#004B4B] rounded border-gray-300 focus:ring-[#004B4B]"
          />
          مشروع مميز (يظهر في الرئيسية)
        </label>
        <label className="flex items-center gap-2 text-sm font-semibold text-[#1B2A4A] cursor-pointer">
          <input
            type="checkbox"
            name="is_published"
            value="true"
            defaultChecked={project?.is_published ?? true}
            className="w-4 h-4 text-[#004B4B] rounded border-gray-300 focus:ring-[#004B4B]"
          />
          منشور
        </label>
      </div>

      <div className="pt-4 border-t border-[#E2E8F0] flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="bg-[#004B4B] text-white px-8 py-2.5 rounded-lg font-bold hover:bg-[#004B4B]/90 transition-colors disabled:opacity-70 flex items-center gap-2 cursor-pointer"
        >
          {loading && (
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          )}
          {loading ? "جارٍ الحفظ والرفع..." : "حفظ المشروع"}
        </button>
      </div>
    </form>
  );
}
