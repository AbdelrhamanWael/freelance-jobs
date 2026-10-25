"use client";

import { useState, useRef } from "react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  // Initialize only on client side to avoid prerender crash
  const supabaseRef = useRef<ReturnType<typeof createClient> | null>(null);
  if (typeof window !== "undefined" && !supabaseRef.current) {
    supabaseRef.current = createClient();
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const supabase = supabaseRef.current;
    if (!supabase) return;

    const trimmedEmail = email.trim().toLowerCase();
    const cleanPassword = password.trim();

    let { error } = await supabase.auth.signInWithPassword({ email: trimmedEmail, password: cleanPassword });

    // Handle BiDi swapped punctuation (e.g. !SecurePassword123 vs SecurePassword123!)
    if (error && (cleanPassword.startsWith("!") || cleanPassword.endsWith("!"))) {
      const altPassword = cleanPassword.startsWith("!")
        ? cleanPassword.slice(1) + "!"
        : "!" + cleanPassword.slice(0, -1);
      const retry = await supabase.auth.signInWithPassword({ email: trimmedEmail, password: altPassword });
      if (!retry.error) {
        error = null;
      }
    }

    if (error) {
      setError("البريد الإلكتروني أو كلمة المرور غير صحيحة");
      setLoading(false);
    } else {
      router.push("/dashboard");
      router.refresh();
    }
  };

  return (
    <div className="min-h-screen bg-[var(--color-secondary)] flex items-center justify-center p-5 dir-rtl font-sans relative overflow-hidden">
      
      {/* Background decoration */}
      <div className="absolute top-0 end-0 w-96 h-96 bg-[var(--color-primary)]/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
      <div className="absolute bottom-0 start-0 w-96 h-96 bg-[var(--color-primary)]/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2"></div>

      <div className="w-full max-w-md relative z-10 animate-fade-in-up">

        {/* Logo */}
        <div className="text-center mb-8">
          <Image 
            src="/Logo-daremmar.png" 
            alt="دار اعمار الغربية" 
            width={200} 
            height={60} 
            className="object-contain h-16 w-auto mx-auto mb-4 drop-shadow-md" 
          />
          <h1 className="text-2xl font-black text-[var(--color-primary)]">نظام الإدارة</h1>
          <p className="text-[var(--color-accent)] text-sm mt-1">دار اعمار الغربية للمقاولات</p>
        </div>

        {/* Login form */}
        <div className="bg-white p-8 rounded-2xl shadow-xl border border-[var(--color-accent)]/10 relative overflow-hidden">
          
          <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-primary)]/50"></div>

          <h2 className="text-lg font-bold text-[var(--color-primary)] mb-6 text-center">تسجيل الدخول</h2>

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-[var(--color-primary)] text-sm font-bold mb-2">
                البريد الإلكتروني
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none text-[var(--color-accent)]/50">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                  </svg>
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="admin@daremmar.com"
                  dir="ltr"
                  className="w-full bg-[#F9F3EC]/30 border border-[var(--color-accent)]/20 text-[var(--color-primary)] text-sm rounded-lg focus:ring-[var(--color-primary)] focus:border-[var(--color-primary)] block ps-10 p-3 transition-colors outline-none"
                  autoComplete="email"
                />
              </div>
            </div>

            <div>
              <label className="block text-[var(--color-primary)] text-sm font-bold mb-2">
                كلمة المرور
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none text-[var(--color-accent)]/50">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  dir="ltr"
                  className="w-full bg-[#F9F3EC]/30 border border-[var(--color-accent)]/20 text-[var(--color-primary)] text-sm rounded-lg focus:ring-[var(--color-primary)] focus:border-[var(--color-primary)] block ps-10 p-3 transition-colors outline-none tracking-widest"
                  autoComplete="current-password"
                />
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3 animate-fade-in">
                <svg className="w-4 h-4 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[var(--color-primary)] hover:bg-[var(--color-primary)]/90 disabled:opacity-70 text-white py-3.5 rounded-lg font-bold transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-[var(--color-primary)]/20 hover:shadow-[var(--color-primary)]/40 hover:-translate-y-0.5"
            >
              {loading ? (
                <>
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  جارٍ الدخول...
                </>
              ) : (
                "دخول"
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-[var(--color-accent)]/60 text-xs mt-6">
          للوصول المصرّح به فقط — دار اعمار الغربية
        </p>
      </div>
    </div>
  );
}
