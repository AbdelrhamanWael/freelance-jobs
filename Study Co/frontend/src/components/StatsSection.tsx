'use client';

import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';

export default function StatsSection() {
  const { i18n } = useTranslation();
  const isRtl = i18n.language === 'ar';

  const stats = isRtl
    ? [
        { icon: '🎓', value: '+500', label: 'جامعة ومعهد شريك' },
        { icon: '🌍', value: '+20', label: 'دولة حول العالم' },
        { icon: '👥', value: '+10,000', label: 'طالب إندونيسي تمت مساعدتهم' },
        { icon: '🛡', value: '95%', label: 'معدل نجاح الفيزا' },
      ]
    : [
        { icon: '🎓', value: '500+', label: 'Universitas Mitra' },
        { icon: '🌍', value: '20+', label: 'Negara Tujuan' },
        { icon: '👥', value: '10.000+', label: 'Pelajar Indonesia Terbantu' },
        { icon: '🛡', value: '95%', label: 'Tingkat Keberhasilan Visa' },
      ];

  return (
    <section className="bg-gray-900 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              className="flex items-center gap-4"
            >
              <div className="w-12 h-12 rounded-xl bg-yellow/15 border border-yellow/30 flex items-center justify-center text-2xl flex-shrink-0">
                {stat.icon}
              </div>
              <div>
                <p className="text-2xl font-black text-white">{stat.value}</p>
                <p className="text-xs text-gray-400 font-medium mt-0.5 leading-tight">{stat.label}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
