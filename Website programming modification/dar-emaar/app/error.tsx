"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service if needed
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-secondary)] p-5 text-center dir-rtl font-sans">
      <div className="max-w-md w-full glass-card p-10 flex flex-col items-center shadow-xl border-t-4 border-t-red-500">
        <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mb-6 text-red-500">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-3">
          عذراً، حدث خطأ غير متوقع!
        </h1>
        <p className="text-[var(--color-accent)] mb-8 text-sm leading-relaxed">
          نعتذر عن هذا الخلل. فريقنا الفني يعمل دائماً لضمان استقرار الموقع. يرجى المحاولة مرة أخرى أو العودة للرئيسية.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 w-full">
          <button
            onClick={() => reset()}
            className="flex-1 bg-[var(--color-primary)] hover:bg-[var(--color-primary)]/90 text-white py-2.5 rounded-sm font-bold text-sm transition-colors shadow-md"
          >
            المحاولة مرة أخرى
          </button>
          <Link
            href="/"
            className="flex-1 border border-[var(--color-primary)] text-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-white py-2.5 rounded-sm font-bold text-sm transition-colors flex items-center justify-center"
          >
            العودة للرئيسية
          </Link>
        </div>
      </div>
    </div>
  );
}
