"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { staggerContainer, fadeInUp, cardHover, buttonPulse } from "@/lib/animations";

import { Building2, Paintbrush, Briefcase } from "lucide-react";
import AnimatedIcon from "@/components/ui/AnimatedIcon";
import type { PageContent } from "@/lib/content";

function parseHighlights(text?: string, fallback: string[] = []): string[] {
  if (!text) return fallback;
  const lines = text
    .split(/[\n,]/)
    .map((s) => s.trim())
    .filter(Boolean);
  return lines.length > 0 ? lines : fallback;
}

export default function Services({ content }: { content?: PageContent }) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });
  const titleRef = useRef<HTMLDivElement>(null);
  const titleInView = useInView(titleRef, { once: true, margin: "-60px" });

  const services = [
    {
      id: "service-1",
      icon: Building2,
      title: content?.service_1_title || "التصميم والبناء",
      description:
        content?.service_1_desc ||
        "تصميم معماري متكامل مع هندسة متخصصة وتنفيذ بجودة عالية وتكلفة تنافسية، من رسم المخططات حتى استلام المفتاح.",
      highlights: parseHighlights(content?.service_1_highlights, [
        "تصميم معماري احترافي",
        "إشراف هندسي متكامل",
        "مواد بناء عالية الجودة",
      ]),
      accent: "#004B4B",
    },
    {
      id: "service-2",
      icon: Paintbrush,
      title: content?.service_2_title || "التشطيبات الداخلية",
      description:
        content?.service_2_desc ||
        "تشطيبات فاخرة تناسب ذوقك وميزانيتك — من الجبس والدهانات حتى الأرضيات والأسقف المعلقة بأعلى المعايير.",
      highlights: parseHighlights(content?.service_2_highlights, [
        "أسقف جبسية وديكور",
        "دهانات وورق جدران",
        "أرضيات وبلاط فاخر",
      ]),
      accent: "#004B4B",
    },
    {
      id: "service-3",
      icon: Briefcase,
      title: content?.service_3_title || "إدارة المشاريع",
      description:
        content?.service_3_desc ||
        "إدارة احترافية كاملة للمشاريع من التخطيط والجدولة الزمنية حتى التسليم النهائي مع ضمان الالتزام بالموعد والميزانية.",
      highlights: parseHighlights(content?.service_3_highlights, [
        "جدولة زمنية دقيقة",
        "تقارير دورية شاملة",
        "تنسيق كامل مع المقاولين",
      ]),
      accent: "#004B4B",
    },
  ];

  const badge = content?.services_badge || "خدماتنا";
  const title = content?.services_title || "ماذا نقدم لك؟";
  const subtitle =
    content?.services_subtitle ||
    "نقدم مجموعة متكاملة من الخدمات الإنشائية تحت سقف واحد — لضمان تجربة بناء سلسة وبلا تعقيد";
  const footerText =
    content?.services_footer_text ||
    "نقدم أيضاً: أعمال الحفر والردم، البنية التحتية، الطاقة المتجددة، خدمات لوجستية، وأكثر من 10 خدمات متخصصة أخرى.";
  const footerCta = content?.services_footer_cta || "تواصل معنا لمعرفة كل خدماتنا ←";

  return (
    <section id="services" className="section-padding bg-[var(--color-secondary)]">
      <div className="container-custom">
        {/* Header */}
        <motion.div
          ref={titleRef}
          initial={{ opacity: 0, y: 30 }}
          animate={titleInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
          className="text-center mb-14"
        >
          <span className="inline-block text-[var(--color-primary)] font-bold text-sm tracking-widest uppercase mb-3">
            {badge}
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-[var(--color-primary)] section-title">
            {title}
          </h2>
          <p className="text-[var(--color-accent)] mt-6 max-w-2xl mx-auto leading-relaxed text-base sm:text-lg">
            {subtitle}
          </p>
        </motion.div>

        {/* Service cards */}
        <motion.div
          ref={ref}
          variants={staggerContainer(0.15)}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12"
        >
          {services.map((service) => (
            <motion.div
              key={service.id}
              variants={{ ...fadeInUp, hover: cardHover.hover, rest: cardHover.rest }}
              initial="rest"
              whileHover="hover"
              animate="visible"
              className="bg-white rounded-2xl overflow-hidden shadow-[0_4px_24px_rgba(4,74,73,0.06)] hover:shadow-[0_12px_32px_rgba(4,74,73,0.12)] transition-all cursor-pointer border border-[var(--color-primary)]/10 flex flex-col justify-between"
            >
              <div>
                {/* Accent band */}
                <div className="h-1.5 w-full bg-[var(--color-primary)]" />

                <div className="p-7">
                  {/* Animated Icon */}
                  <div className="w-14 h-14 rounded-xl bg-[var(--color-primary)]/5 flex items-center justify-center text-[var(--color-primary)] mb-5">
                    <AnimatedIcon icon={service.icon} size={28} />
                  </div>

                  <h3 className="text-xl font-bold text-[var(--color-primary)] mb-3">{service.title}</h3>
                  <p className="text-[var(--color-accent)] text-sm leading-relaxed mb-6">{service.description}</p>

                  <ul className="space-y-2.5 mb-6">
                    {service.highlights.map((h, i) => (
                      <motion.li
                        key={i}
                        initial={{ opacity: 0, x: 10 }}
                        animate={isInView ? { opacity: 1, x: 0 } : {}}
                        transition={{ delay: 0.3 + i * 0.08 }}
                        className="flex items-center gap-2.5 text-sm text-[var(--color-accent)] font-medium"
                      >
                        <span className="w-2 h-2 rounded-full flex-shrink-0 bg-[var(--color-primary)]" />
                        {h}
                      </motion.li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="px-7 pb-7 pt-2 border-t border-gray-100/80">
                <motion.a
                  href="#contact"
                  variants={buttonPulse}
                  initial="rest"
                  whileHover="hover"
                  whileTap="tap"
                  className="inline-flex items-center gap-2 font-bold text-sm text-[var(--color-primary)] hover:underline"
                >
                  اطلب هذه الخدمة
                  <svg className="w-4 h-4 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
                  </svg>
                </motion.a>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* View all / Footer note */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ delay: 0.6 }}
          className="text-center bg-white/60 backdrop-blur-sm p-6 rounded-2xl border border-[var(--color-primary)]/10 max-w-3xl mx-auto shadow-sm"
        >
          <p className="text-[var(--color-accent)] text-sm sm:text-base leading-relaxed mb-2 font-medium">
            {footerText}
          </p>
          <a
            href="#contact"
            className="text-[var(--color-primary)] font-bold text-sm sm:text-base inline-flex items-center gap-1.5 hover:underline"
          >
            {footerCta}
          </a>
        </motion.div>
      </div>
    </section>
  );
}
