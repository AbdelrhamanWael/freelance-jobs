"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useInView } from "framer-motion";
import { staggerContainer, scaleIn } from "@/lib/animations";

type Stat = {
  id: string;
  label: string;
  value: string;
  sort_order: number;
};

function parseValue(raw: string): { number: number; suffix: string } {
  // Extract numeric part and suffix from strings like "15+", "200+", "98%", "50+"
  const match = raw.match(/^(\d+)(.*)$/);
  if (match) {
    return { number: parseInt(match[1], 10), suffix: match[2] || "" };
  }
  return { number: 0, suffix: raw };
}

function useCounter(target: number, started: boolean) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!started) return;
    const duration = 2000;
    const steps = 60;
    const increment = target / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) { setCount(target); clearInterval(timer); }
      else setCount(Math.floor(current));
    }, duration / steps);
    return () => clearInterval(timer);
  }, [target, started]);
  return count;
}

const ICONS = [
  // Experience / Award
  <svg key="0" className="w-8 h-8 text-[var(--color-primary)] mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
  </svg>,
  // Projects / Building
  <svg key="1" className="w-8 h-8 text-[var(--color-primary)] mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
  </svg>,
  // Clients / People
  <svg key="2" className="w-8 h-8 text-[var(--color-primary)] mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
  </svg>,
  // Satisfaction / Star
  <svg key="3" className="w-8 h-8 text-[var(--color-primary)] mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
  </svg>,
  // Chart / Stats
  <svg key="4" className="w-8 h-8 text-[var(--color-primary)] mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>,
];

function StatCard({ label, value, index, started }: { label: string; value: string; index: number; started: boolean }) {
  const { number, suffix } = parseValue(value);
  const count = useCounter(number, started);

  return (
    <motion.div
      variants={scaleIn}
      custom={index}
      className="text-center group"
    >
      <motion.div
        animate={started ? { scale: [0.8, 1.1, 1] } : { scale: 0.8 }}
        transition={{ duration: 0.5, delay: index * 0.1 }}
        className="text-3xl mb-2"
      >
        {ICONS[index % ICONS.length]}
      </motion.div>
      <div className="text-4xl font-black text-[var(--color-accent)] mb-1">
        <motion.span
          initial={{ opacity: 0 }}
          animate={started ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
        >
          {number > 0 ? count : value}
        </motion.span>
        {number > 0 && <span className="text-[var(--color-primary)]">{suffix}</span>}
      </div>
      <p className="text-[var(--color-accent)]/80 font-medium text-sm">{label}</p>
    </motion.div>
  );
}

export default function TrustBar({ stats }: { stats: Stat[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  if (!stats || stats.length === 0) return null;

  const cols = stats.length <= 2 ? stats.length : stats.length <= 3 ? 3 : 4;

  return (
    <section ref={ref} className="bg-[var(--color-secondary)] py-12 border-y border-[var(--color-accent)]/20 overflow-hidden">
      <div className="container-custom">
        <motion.div
          variants={staggerContainer(0.15)}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          className={`grid grid-cols-2 lg:grid-cols-${cols} gap-8`}
        >
          {stats.map((stat, i) => (
            <StatCard key={stat.id} label={stat.label} value={stat.value} index={i} started={isInView} />
          ))}
        </motion.div>
      </div>
    </section>
  );
}
