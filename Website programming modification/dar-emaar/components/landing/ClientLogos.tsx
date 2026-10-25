"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { staggerContainer, scaleIn, fadeInUp } from "@/lib/animations";
import type { DbClient } from "@/lib/db-clients";

const fallbackClients: Partial<DbClient>[] = [
  { name: "Axalines" }, { name: "ERAM" }, { name: "Saudi Investment Bank" },
  { name: "Simya" }, { name: "ADB" }, { name: "KWIN" },
  { name: "عمار العقارية" }, { name: "الديار" }, { name: "المملكة هولدينج" },
  { name: "إتقان" }, { name: "التطوير العمراني" }, { name: "البناء الحديث" },
];

export default function ClientLogos({ dbClients = [] }: { dbClients?: DbClient[] }) {
  const clientsToDisplay = dbClients.length > 0 ? dbClients : fallbackClients;

  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });
  const titleRef = useRef<HTMLDivElement>(null);
  const titleInView = useInView(titleRef, { once: true });
  const certRef = useRef<HTMLDivElement>(null);
  const certInView = useInView(certRef, { once: true });

  return (
    <section id="clients" className="section-padding bg-[var(--color-secondary)]">
      <div className="container-custom">

        {/* Header */}
        <motion.div
          ref={titleRef}
          initial={{ opacity: 0, y: 30 }}
          animate={titleInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
          className="text-center mb-12"
        >
          <span className="inline-block text-[var(--color-primary)] font-bold text-sm tracking-widest uppercase mb-3">عملاؤنا</span>
          <h2 className="text-3xl sm:text-4xl font-black text-[var(--color-primary)] section-title">
            شركاء النجاح
          </h2>
          <p className="text-[var(--color-accent)] mt-6 max-w-xl mx-auto leading-relaxed">
            نفخر بثقة كبرى الشركات والمؤسسات التي اختارت دار اعمار الغربية شريكاً في مشاريعها
          </p>
        </motion.div>

        {/* Logo grid — staggered pop-in */}
        <motion.div
          ref={ref}
          variants={staggerContainer(0.06)}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-4"
        >
          {clientsToDisplay.map((client, i) => (
            <motion.div
              key={client.id || client.name}
              variants={scaleIn}
              whileHover={{
                scale: 1.06,
                borderColor: "rgba(0,75,75,0.5)",
                boxShadow: "0 4px 20px rgba(0,75,75,0.15)",
              }}
              transition={{ duration: 0.2 }}
              className="aspect-[3/2] bg-white border border-[#E2E8F0] rounded-sm flex items-center justify-center p-4 cursor-pointer overflow-hidden relative group"
            >
              {client.logo_url ? (
                <img 
                  src={client.logo_url} 
                  alt={client.name} 
                  className="w-full h-full object-contain filter grayscale group-hover:grayscale-0 transition-all duration-300" 
                />
              ) : (
                <motion.span
                  whileHover={{ color: "#004B4B" }}
                  className="text-[var(--color-accent)] text-xs font-bold text-center leading-tight transition-colors"
                >
                  {client.name}
                </motion.span>
              )}
            </motion.div>
          ))}
        </motion.div>

        {/* Certifications — slide up from bottom */}
        <motion.div
          ref={certRef}
          initial={{ opacity: 0, y: 25 }}
          animate={certInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-12 text-center"
        >
          <p className="text-[var(--color-accent)] text-sm font-medium mb-4">معتمدون ومرخصون من</p>
          <motion.div
            variants={staggerContainer(0.12)}
            initial="hidden"
            animate={certInView ? "visible" : "hidden"}
            className="flex flex-wrap items-center justify-center gap-6"
          >
            {["وزارة الشؤون البلدية", "هيئة المقاولين", "الغرفة التجارية"].map((cert) => (
              <motion.div
                key={cert}
                variants={fadeInUp}
                className="flex items-center gap-2 text-[var(--color-accent)] text-sm"
              >
                <motion.svg
                  className="w-4 h-4 text-[var(--color-primary)]"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  whileHover={{ scale: 1.3, rotate: 10 }}
                >
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </motion.svg>
                {cert}
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

      </div>
    </section>
  );
}
