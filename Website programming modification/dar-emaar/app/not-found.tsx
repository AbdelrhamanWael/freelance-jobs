import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-[var(--color-secondary)] p-5 text-center dir-rtl font-sans">
      <div className="max-w-md w-full flex flex-col items-center">
        <h1 className="text-9xl font-black text-[var(--color-primary)] opacity-20 mb-4 select-none">
          404
        </h1>
        <h2 className="text-3xl font-bold text-[var(--color-primary)] mb-3">
          الصفحة غير موجودة
        </h2>
        <p className="text-[var(--color-accent)] mb-8 text-sm leading-relaxed">
          يبدو أن الرابط الذي تحاول الوصول إليه غير صحيح، أو تم نقل الصفحة أو حذفها. لا تقلق، يمكنك العودة للصفحة الرئيسية واستكشاف خدماتنا.
        </p>
        <Link
          href="/"
          className="bg-[var(--color-primary)] hover:bg-[var(--color-primary)]/90 text-white px-8 py-3 rounded-sm font-bold text-sm transition-all shadow-[0_4px_14px_rgba(0,75,75,0.35)] hover:shadow-[0_4px_20px_rgba(0,75,75,0.5)] hover:-translate-y-px flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          العودة للرئيسية
        </Link>
      </div>
    </div>
  );
}
