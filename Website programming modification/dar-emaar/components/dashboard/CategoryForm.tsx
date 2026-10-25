"use client";

import { useState } from "react";
import { saveCategory } from "@/app/actions/categories";
import { useRouter } from "next/navigation";

export default function CategoryForm({ category }: { category?: any }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [name, setName] = useState(category?.name || "");
  const [slug, setSlug] = useState(category?.slug || "");
  const [slugTouched, setSlugTouched] = useState(!!category?.slug);

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

  function handleNameChange(e: React.ChangeEvent<HTMLInputElement>) {
    const newName = e.target.value;
    setName(newName);
    if (!slugTouched) {
      setSlug(generateSlug(newName));
    }
  }

  function handleSlugChange(e: React.ChangeEvent<HTMLInputElement>) {
    setSlug(e.target.value);
    setSlugTouched(true);
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const formData = new FormData(e.currentTarget);
    const result = await saveCategory(formData);

    if (result?.error) {
      setError(result.error);
      setLoading(false);
    } else {
      router.push("/dashboard/categories");
      router.refresh();
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-200">
          {error}
        </div>
      )}

      {category?.id && <input type="hidden" name="id" value={category.id} />}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">اسم الفئة *</label>
          <input
            name="name"
            value={name}
            onChange={handleNameChange}
            required
            className="form-input-light"
            placeholder="مثال: التصميم المعماري"
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
            dir="ltr"
            placeholder="architectural-design"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">ترتيب العرض</label>
          <input
            type="number"
            name="sort_order"
            defaultValue={category?.sort_order ?? 99}
            className="form-input-light"
            placeholder="رقم الترتيب (مثل 1, 2, 3)"
          />
        </div>
      </div>

      <div className="pt-4 border-t border-[#E2E8F0] flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="bg-[var(--color-primary)] text-white px-8 py-2.5 rounded-lg font-bold hover:bg-[var(--color-primary)]/90 transition-colors disabled:opacity-70 flex items-center gap-2"
        >
          {loading && (
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          )}
          حفظ الفئة
        </button>
      </div>
    </form>
  );
}
