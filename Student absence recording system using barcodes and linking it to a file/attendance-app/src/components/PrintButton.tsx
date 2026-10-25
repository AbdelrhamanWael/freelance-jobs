'use client'

import { Printer } from "lucide-react";

export default function PrintButton() {
  return (
    <button
      onClick={() => window.print()}
      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors cursor-pointer"
    >
      <Printer size={18} />
      طباعة الكل
    </button>
  );
}
