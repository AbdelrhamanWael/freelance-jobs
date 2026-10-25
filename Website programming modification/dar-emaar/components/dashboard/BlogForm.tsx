"use client";

import { useState } from "react";
import { saveBlogPost } from "@/app/actions/blog";
import { useRouter } from "next/navigation";

export default function BlogForm({ post }: { post?: any }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [title, setTitle] = useState(post?.title || "");
  const [slug, setSlug] = useState(post?.slug || "");
  const [slugTouched, setSlugTouched] = useState(!!post?.slug);
  const [coverImageUrl, setCoverImageUrl] = useState(
    post?.cover_image && !post.cover_image.startsWith("file:") ? post.cover_image : ""
  );
  const [imagePreview, setImagePreview] = useState<string | null>(
    post?.cover_image && !post.cover_image.startsWith("file:") ? post.cover_image : null
  );

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

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setImagePreview(url);
    }
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const formData = new FormData(e.currentTarget);
    const result = await saveBlogPost(formData);

    if (result?.error) {
      setError(result.error);
      setLoading(false);
    } else {
      router.push("/dashboard/blog");
      router.refresh();
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-200">
          {error}
        </div>
      )}

      {post?.id && <input type="hidden" name="id" value={post.id} />}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">عنوان المقال *</label>
          <input
            name="title"
            value={title}
            onChange={handleTitleChange}
            required
            className="form-input-light"
            placeholder="مثال: دليل التشطيبات الفاخرة"
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
            placeholder="example-blog-slug أو التشطيبات"
          />
          <p className="text-xs text-gray-500 mt-1">يمكن أن يكون باللغة العربية أو الإنجليزية (مثال: التشطيبات أو finishing-guide)</p>
        </div>

        {/* Cover Image Section: File Upload + Direct URL */}
        <div className="md:col-span-2 bg-[#F8FAFC] p-4 sm:p-5 rounded-xl border border-[#E2E8F0] space-y-3">
          <label className="block text-sm font-bold text-[#1B2A4A]">صورة غلاف المقال</label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="block text-xs font-semibold text-gray-700 mb-1.5">١. رفع صورة مباشرة من جهازك (مستحسن)</span>
              <input
                type="file"
                name="cover_file"
                accept="image/*"
                onChange={handleFileChange}
                className="block w-full text-xs text-gray-500 file:mr-0 file:ml-3 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-[#004B4B] file:text-white hover:file:bg-[#003838] cursor-pointer bg-white p-1.5 rounded-lg border border-gray-200"
              />
              <p className="text-[11px] text-gray-500 mt-1">اختر ملف صورة وسيتم حفظه وعرضه تلقائياً في الموقع</p>
            </div>
            <div>
              <span className="block text-xs font-semibold text-gray-700 mb-1.5">٢. أو رابط صورة خارجي (اختياري)</span>
              <input
                name="cover_image"
                value={coverImageUrl}
                onChange={(e) => {
                  setCoverImageUrl(e.target.value);
                  setImagePreview(e.target.value);
                }}
                className="form-input-light text-left"
                dir="ltr"
                placeholder="https://... أو /انتيرنال-ماركيتينق-1.jpg"
              />
            </div>
          </div>
          {(imagePreview || coverImageUrl) && (
            <div className="pt-2 flex items-center gap-3 border-t border-gray-200/60 mt-2">
              <span className="text-xs font-semibold text-gray-600">معاينة الغلاف:</span>
              <div className="h-16 w-28 rounded-lg overflow-hidden border border-gray-300 relative bg-gray-100 shadow-sm">
                <img
                  src={imagePreview || coverImageUrl}
                  alt="معاينة"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          )}
        </div>

        {/* Author Section */}
        <div className="md:col-span-2 bg-[#F8FAFC] p-4 sm:p-5 rounded-xl border border-[#E2E8F0] space-y-4">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-bold text-[#1B2A4A]">معلومات الكاتب (صندوق الكاتب أسفل المقال)</label>
            <span className="text-xs text-[#004B4B] font-semibold bg-[#004B4B]/10 px-2 py-0.5 rounded">قابلة للتعديل بالكامل</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">اسم الكاتب</label>
              <input
                name="author"
                defaultValue={post?.author || "فريق دار اعمار الغربية"}
                className="form-input-light"
                placeholder="مثال: م. أديب العامودي أو فريق دار اعمار الغربية"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">المسمى / الصفة الوظيفية</label>
              <input
                name="author_title"
                defaultValue={post?.author_title || "قسم الهندسة والمحتوى المعماري"}
                className="form-input-light"
                placeholder="مثال: قسم الهندسة والتصميم أو مهندس استشاري"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-gray-700 mb-1">نبذة عن الكاتب / التوقيع</label>
              <textarea
                name="author_bio"
                defaultValue={post?.author_bio || "نشارككم خبراتنا الميدانية وأحدث الأفكار والحلول الهندسية في مجالات المقاولات العامة والتشطيبات الفاخرة وإدارة المشاريع بالمملكة العربية السعودية."}
                rows={2}
                className="form-input-light min-h-[60px]"
                placeholder="اكتب نبذة تعريفية بالكاتب تظهر ببطاقة التوقيع أسفل المقال..."
              />
            </div>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">نبذة مختصرة (تظهر في بطاقة المقال بالرئيسية)</label>
        <textarea
          name="excerpt"
          defaultValue={post?.excerpt}
          rows={2}
          className="form-input-light min-h-[60px]"
          placeholder="نبذة سريعة تلخص محتوى المقال في سطرين..."
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">محتوى المقال (يدعم كود HTML)</label>
        <textarea
          name="content"
          defaultValue={post?.content}
          rows={10}
          className="form-input-light min-h-[250px] text-right"
          dir="rtl"
          placeholder="اكتب نص المقال هنا..."
        />
      </div>

      <div className="flex gap-6">
        <label className="flex items-center gap-2 text-sm font-semibold text-[#1B2A4A] cursor-pointer">
          <input
            type="checkbox"
            name="is_published"
            value="true"
            defaultChecked={post?.is_published ?? true}
            className="w-4 h-4 text-[#004B4B] rounded border-gray-300 focus:ring-[#004B4B]"
          />
          نشر المقال (يظهر للزوار في الموقع)
        </label>
      </div>

      <div className="pt-4 border-t border-[#E2E8F0] flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="bg-[#004B4B] text-white px-8 py-2.5 rounded-lg font-bold hover:bg-[#004B4B]/90 transition-colors disabled:opacity-70 flex items-center gap-2"
        >
          {loading && (
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          )}
          حفظ المقال
        </button>
      </div>
    </form>
  );
}
