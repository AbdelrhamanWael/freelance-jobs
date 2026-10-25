"use client";

import { useActionState, useEffect, useRef } from "react";
import { motion, AnimatePresence, useInView } from "framer-motion";
import { submitLead, type LeadFormState } from "@/app/actions/leads";
import { staggerContainer, fadeInUp, buttonPulse, scaleIn } from "@/lib/animations";
import { Send, CheckCircle2, PhoneCall } from "lucide-react";

const DEFAULT_SERVICES = [
  "التصميم والبناء",
  "اعمال الحفر والاحلال",
  "الهيكل الانشائي",
  "الالكتروميكانيك",
  "التشطيبات الداخلية والخارجية",
];

const initialState: LeadFormState = { success: false };

function SubmitButton({ pending }: { pending: boolean }) {
  return (
    <motion.button
      type="submit"
      disabled={pending}
      variants={buttonPulse}
      initial="rest"
      whileHover={pending ? "rest" : "hover"}
      whileTap={pending ? "rest" : "tap"}
      className="w-full bg-[var(--color-primary)] hover:bg-[var(--color-primary)]/90 disabled:opacity-70 disabled:cursor-not-allowed text-white py-4 rounded-sm text-lg font-bold shadow-[0_8px_24px_rgba(0,75,75,0.2)] flex items-center justify-center gap-3"
    >
      {pending ? (
        <>
          <motion.svg
            className="w-5 h-5"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </motion.svg>
          جارٍ الإرسال...
        </>
      ) : (
        <>
          <Send className="w-5 h-5 rtl:-scale-x-100" strokeWidth={2.5} />
          أرسل طلبك الآن — مجاناً
        </>
      )}
    </motion.button>
  );
}

export default function LeadForm({ services }: { services?: string[] }) {
  const activeServices = services && services.length > 0 ? services : DEFAULT_SERVICES;
  const [state, formAction, isPending] = useActionState(submitLead, initialState);
  const formRef = useRef<HTMLFormElement>(null);
  const sectionRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(sectionRef, { once: true, margin: "-80px" });

  useEffect(() => {
    if (state.success) formRef.current?.reset();
  }, [state.success]);

  return (
    <section id="contact" ref={sectionRef} className="section-padding bg-[var(--color-secondary)] relative overflow-hidden">

      {/* Animated background orbs */}
      <motion.div
        animate={{ scale: [1, 1.2, 1], opacity: [0.03, 0.06, 0.03] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-0 end-0 w-96 h-96 bg-[var(--color-accent)] rounded-full blur-3xl translate-x-1/2 -translate-y-1/2 pointer-events-none"
      />
      <motion.div
        animate={{ scale: [1, 1.15, 1], opacity: [0.02, 0.05, 0.02] }}
        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 3 }}
        className="absolute bottom-0 start-0 w-96 h-96 bg-[var(--color-accent)] rounded-full blur-3xl -translate-x-1/2 translate-y-1/2 pointer-events-none"
      />

      <div className="container-custom relative z-10">
        <div className="max-w-2xl mx-auto">

          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 35 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="text-center mb-10"
          >
            <span className="inline-block text-[var(--color-primary)] font-bold text-sm tracking-widest uppercase mb-3">اتصل بنا</span>
            <h2 className="text-3xl sm:text-4xl font-black text-[var(--color-primary)] section-title">
              احصل على عرض سعر مجاني
            </h2>
            <motion.p
              initial={{ opacity: 0 }}
              animate={isInView ? { opacity: 1 } : {}}
              transition={{ delay: 0.3 }}
              className="text-[var(--color-accent)] font-semibold mt-6 text-lg"
            >
              نرد خلال 24 ساعة — استشارة أولى بدون أي التزام
            </motion.p>
            <p className="text-[var(--color-accent)]/70 text-sm mt-2">
              أكثر من 200 مشروع منجز. قل لنا عن مشروعك وسنرد عليك فوراً.
            </p>
          </motion.div>

          {/* Form / Success — AnimatePresence for smooth state swap */}
          <AnimatePresence mode="wait">
            {state.success ? (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                className="glass-card p-10 text-center"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, damping: 14, delay: 0.1 }}
                  className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-5"
                >
                  <motion.svg
                    className="w-10 h-10 text-green-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </motion.svg>
                </motion.div>
                <h3 className="text-2xl font-bold text-[var(--color-primary)] mb-3">تم استلام طلبك! ✅</h3>
                <p className="text-[var(--color-accent)] leading-relaxed mb-6">
                  شكراً لتواصلك مع دار اعمار الغربية. سيقوم فريقنا بالتواصل معك في أقرب وقت ممكن، عادةً خلال 24 ساعة.
                </p>
                <button
                  onClick={() => window.location.reload()}
                  className="text-[var(--color-primary)] font-semibold text-sm hover:underline"
                >
                  إرسال طلب آخر
                </button>
              </motion.div>
            ) : (
              <motion.form
                key="form"
                ref={formRef}
                action={formAction}
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.6, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
                className="glass-card p-8 space-y-5"
              >
                <input type="hidden" name="source" value="quote_form" />

                {/* Fields animate in staggered */}
                <motion.div
                  variants={staggerContainer(0.08, 0.3)}
                  initial="hidden"
                  animate={isInView ? "visible" : "hidden"}
                  className="grid grid-cols-1 sm:grid-cols-2 gap-5"
                >
                  <motion.div variants={fadeInUp}>
                    <label className="block text-[var(--color-accent)] text-sm font-semibold mb-2">
                      الاسم الكامل <span className="text-red-500">*</span>
                    </label>
                    <input type="text" name="name" required minLength={2} placeholder="اكتب اسمك هنا" className="form-input" autoComplete="name" />
                  </motion.div>
                  <motion.div variants={fadeInUp}>
                    <label className="block text-[var(--color-accent)] text-sm font-semibold mb-2">
                      رقم الجوال <span className="text-red-500">*</span>
                    </label>
                    <input type="tel" name="phone" required placeholder="05xxxxxxxx" inputMode="tel" dir="ltr" className="form-input text-start" autoComplete="tel" />
                  </motion.div>
                </motion.div>

                <motion.div variants={fadeInUp} initial="hidden" animate={isInView ? "visible" : "hidden"} transition={{ delay: 0.45 }}>
                  <label htmlFor="service-select" className="block text-[var(--color-accent)] text-sm font-semibold mb-2">الخدمة المطلوبة</label>
                  <select id="service-select" name="service" aria-label="اختر الخدمة المطلوبة" className="form-input appearance-none cursor-pointer" defaultValue="">
                    <option value="" disabled>اختر الخدمة المناسبة لك</option>
                    {activeServices.map((s: string) => (
                      <option key={s} value={s} className="bg-white text-[var(--color-primary)]">{s}</option>
                    ))}
                  </select>
                </motion.div>

                <motion.div variants={fadeInUp} initial="hidden" animate={isInView ? "visible" : "hidden"} transition={{ delay: 0.53 }}>
                  <label className="block text-[var(--color-accent)] text-sm font-semibold mb-2">
                    تفاصيل المشروع <span className="text-[var(--color-accent)]/60 font-normal text-xs">(اختياري)</span>
                  </label>
                  <textarea name="message" rows={4} placeholder="صف مشروعك باختصار — الموقع، المساحة، أي تفاصيل تساعدنا على تقديم عرض دقيق..." className="form-input resize-none" />
                </motion.div>

                {/* Error */}
                <AnimatePresence>
                  {state.error && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="flex items-center gap-2 bg-red-500/15 border border-red-500/30 rounded-lg px-4 py-3 overflow-hidden"
                    >
                      <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <p className="text-red-300 text-sm font-medium">{state.error}</p>
                    </motion.div>
                  )}
                </AnimatePresence>

                <SubmitButton pending={isPending} />

                {/* Trust micro-copy */}
                <motion.div
                  variants={staggerContainer(0.1, 0.7)}
                  initial="hidden"
                  animate={isInView ? "visible" : "hidden"}
                  className="flex flex-wrap items-center justify-center gap-5 pt-2"
                >
                  {["معلوماتك محمية وآمنة", "بدون أي التزام مسبق", "رد خلال 24 ساعة"].map((item) => (
                    <motion.div key={item} variants={fadeInUp} className="flex items-center gap-1.5 text-[var(--color-accent)] text-xs font-medium">
                      <CheckCircle2 className="w-4 h-4 text-[var(--color-primary)]" />
                      {item}
                    </motion.div>
                  ))}
                </motion.div>
              </motion.form>
            )}
          </AnimatePresence>

          <motion.div
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            transition={{ delay: 0.8 }}
            className="text-center mt-8"
          >
            <p className="text-[var(--color-accent)]/70 text-sm mb-3">أو تواصل معنا مباشرة</p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <motion.a href="tel:+966500000000" whileHover={{ scale: 1.05, color: "#004B4B" }} className="flex items-center gap-2 text-[var(--color-accent)] font-semibold transition-colors">
                <PhoneCall className="w-5 h-5" strokeWidth={2} />
                <span dir="ltr">+966 50 000 0000</span>
              </motion.a>
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}
