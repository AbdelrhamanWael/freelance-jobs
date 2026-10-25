"use client";

import { deleteCategory } from "@/app/actions/categories";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function DeleteCategoryButton({ id, name }: { id: string; name: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleDelete() {
    if (!confirm(`هل أنت متأكد من حذف فئة "${name}"؟ سيتم إزالتها من أي مشاريع مرتبطة بها.`)) return;
    setLoading(true);
    await deleteCategory(id);
    router.refresh();
    setLoading(false);
  }

  return (
    <button
      onClick={handleDelete}
      disabled={loading}
      className="text-red-500 hover:text-red-700 font-medium disabled:opacity-50"
    >
      {loading ? "جاري الحذف..." : "حذف"}
    </button>
  );
}
