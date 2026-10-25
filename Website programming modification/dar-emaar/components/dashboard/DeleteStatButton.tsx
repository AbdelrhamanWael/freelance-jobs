"use client";

import { deleteStat } from "@/app/actions/stats";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function DeleteStatButton({ id, label }: { id: string; label: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleDelete() {
    if (!confirm(`هل أنت متأكد من حذف خانة "${label}"؟`)) return;
    setLoading(true);
    await deleteStat(id);
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
