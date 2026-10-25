"use client";

import { useActionState, useState } from "react";
import { saveClient } from "@/app/actions/clients";
import { useRouter } from "next/navigation";
import { UploadCloud, Save, X, AlertCircle } from "lucide-react";
import type { DbClient } from "@/lib/db-clients";

const initialState: any = {};

export default function ClientForm({ client }: { client?: DbClient }) {
  const [state, action, isPending] = useActionState(saveClient, initialState);
  const router = useRouter();
  const [previewImage, setPreviewImage] = useState<string | null>(client?.logo_url || null);

  // If successfully saved, navigate back
  if (state.success) {
    router.push("/dashboard/clients");
    router.refresh();
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewImage(url);
    }
  };

  return (
    <form action={action} className="bg-white rounded-xl shadow-sm border border-[#E2E8F0] p-6 max-w-2xl">
      <input type="hidden" name="id" value={client?.id || "new"} />
      <input type="hidden" name="logo_url" value={client?.logo_url || ""} />

      {state.error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 flex items-center gap-2 text-sm">
          <AlertCircle className="w-5 h-5" />
          {state.error}
        </div>
      )}

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-2">اسم العميل <span className="text-red-500">*</span></label>
          <input
            type="text"
            name="name"
            defaultValue={client?.name}
            required
            className="w-full px-4 py-2 border border-[#E2E8F0] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
            placeholder="مثال: شركة أكسالينز"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-[#1B2A4A] mb-2">شعار العميل (يفضل مفرغ بخلفية شفافة)</label>
          <div className="flex flex-col sm:flex-row items-start gap-4">
            <div className="flex-1 w-full relative">
              <input
                type="file"
                name="logo_file"
                accept="image/png, image/jpeg, image/svg+xml, image/webp"
                onChange={handleImageChange}
                className="hidden"
                id="logo_file_input"
              />
              <label
                htmlFor="logo_file_input"
                className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-[#E2E8F0] rounded-xl hover:border-[#004B4B] hover:bg-[#F8FAFC] transition-colors cursor-pointer"
              >
                <UploadCloud className="w-8 h-8 text-[#64748B] mb-2" />
                <span className="text-sm text-[#64748B] font-medium">اضغط لرفع الشعار</span>
                <span className="text-xs text-[#94A3B8] mt-1">PNG, SVG, WEBP أو JPEG</span>
              </label>
            </div>
            {previewImage && (
              <div className="relative w-32 h-32 border border-[#E2E8F0] rounded-xl bg-[#F8FAFC] flex items-center justify-center overflow-hidden flex-shrink-0 group">
                <img src={previewImage} alt="Preview" className="max-w-full max-h-full object-contain p-2" />
                <button
                  type="button"
                  onClick={() => {
                    setPreviewImage(null);
                    const fileInput = document.getElementById('logo_file_input') as HTMLInputElement;
                    if (fileInput) fileInput.value = '';
                    const hiddenInput = document.querySelector('input[name="logo_url"]') as HTMLInputElement;
                    if (hiddenInput) hiddenInput.value = '';
                  }}
                  className="absolute top-1 right-1 bg-white rounded-full p-1 shadow-md text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold text-[#1B2A4A] mb-2">الترتيب</label>
            <input
              type="number"
              name="sort_order"
              defaultValue={client?.sort_order || 0}
              className="w-full px-4 py-2 border border-[#E2E8F0] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#004B4B]/20"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-[#1B2A4A] mb-2">الحالة</label>
            <div className="flex items-center gap-3 mt-3">
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="hidden"
                  name="is_published"
                  value={client ? (client.is_published ? "true" : "false") : "true"}
                />
                <input
                  type="checkbox"
                  defaultChecked={client ? client.is_published : true}
                  onChange={(e) => {
                    const hidden = document.querySelector<HTMLInputElement>('input[name="is_published"]');
                    if (hidden) hidden.value = e.target.checked ? "true" : "false";
                  }}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-[#E2E8F0] peer-focus:ring-2 peer-focus:ring-[#004B4B]/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#004B4B]" />
              </label>
              <span className="text-sm text-[#64748B]">ظاهر في الموقع</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 pt-6 border-t border-[#E2E8F0] flex justify-end gap-3">
        <button
          type="button"
          onClick={() => router.push("/dashboard/clients")}
          className="px-6 py-2 border border-[#E2E8F0] rounded-lg text-sm font-semibold text-[#64748B] hover:bg-[#F8FAFC] transition-colors"
        >
          إلغاء
        </button>
        <button
          type="submit"
          disabled={isPending}
          className="bg-[#004B4B] hover:bg-[#004B4B]/90 disabled:opacity-60 text-white px-8 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 shadow-md shadow-[#004B4B]/20"
        >
          {isPending ? "جارٍ الحفظ..." : <><Save className="w-4 h-4" /> حفظ العميل</>}
        </button>
      </div>
    </form>
  );
}
