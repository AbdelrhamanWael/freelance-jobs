"use client";

import { useState } from "react";
import { saveStat } from "@/app/actions/stats";
import { useRouter } from "next/navigation";

export default function StatForm({ stat }: { stat?: any }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");
    const formData = new FormData(e.currentTarget);
    const result = await saveStat(formData);
    if (result?.error) {
      setError(result.error);
      setLoading(false);
    } else {
      router.push("/dashboard/stats");
      router.refresh();
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-200">{error}</div>
      )}
      {stat?.id && <input type="hidden" name="id" value={stat.id} />}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">
            اسم الخانة (التسمية) *
          </label>
          <input
            name="label"
            defaultValue={stat?.label}
            required
            className="form-input-light"
            placeholder="مثال: سنة خبرة"
          />
          <p className="text-xs text-[#94A3B8] mt-1">هذا هو النص الذي يظهر أسفل الرقم في الموقع</p>
        </div>

        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">
            القيمة / الرقم *
          </label>
          <input
            name="value"
            defaultValue={stat?.value}
            required
            className="form-input-light"
            placeholder="مثال: 15+ أو 98%"
            dir="ltr"
          />
          <p className="text-xs text-[#94A3B8] mt-1">يمكن أن يحتوي على رموز مثل + أو %</p>
        </div>

        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-1.5">ترتيب الظهور</label>
          <input
            type="number"
            name="sort_order"
            defaultValue={stat?.sort_order ?? 99}
            className="form-input-light"
            placeholder="1, 2, 3 ..."
          />
        </div>

        <div className="flex items-center">
          <label className="flex items-center gap-3 cursor-pointer mt-4">
            <input
              type="hidden"
              name="is_visible"
              value="false"
            />
            <input
              type="checkbox"
              name="is_visible"
              value="true"
              defaultChecked={stat?.is_visible ?? true}
              className="w-5 h-5 text-[var(--color-primary)] rounded border-gray-300 focus:ring-[var(--color-primary)]"
              onChange={(e) => {
                const hidden = e.currentTarget.previousElementSibling as HTMLInputElement;
                hidden.disabled = e.currentTarget.checked;
              }}
            />
            <div>
              <span className="text-sm font-semibold text-[#1B2A4A]">ظاهر في الموقع</span>
              <p className="text-xs text-[#94A3B8]">إلغاء التحديد لإخفاء هذه الخانة</p>
            </div>
          </label>
        </div>
      </div>

      <div className="pt-4 border-t border-[#E2E8F0] flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="bg-[var(--color-primary)] text-white px-8 py-2.5 rounded-lg font-bold hover:bg-[var(--color-primary)]/90 transition-colors disabled:opacity-70 flex items-center gap-2"
        >
          {loading && (
            <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          )}
          حفظ الخانة
        </button>
      </div>
    </form>
  );
}
