'use client';

import { useTranslation } from 'react-i18next';

const LOGOS = [
  { name: "TAYLOR'S UNIVERSITY", color: '#8B1A1A' },
  { name: "SUNWAY UNIVERSITY",   color: '#003087' },
  { name: "MONASH University",   color: '#006DAE' },
  { name: "THE UNIVERSITY OF SYDNEY", color: '#CC0000' },
  { name: "DEAKIN UNIVERSITY",   color: '#000000' },
  { name: "UNIVERSITY OF TORONTO", color: '#002A5C' },
];

export default function PartnersSection() {
  const { i18n } = useTranslation();
  const isRtl = i18n.language === 'ar';

  const title = isRtl ? 'شركاؤنا من الجامعات' : 'Universitas Mitra Kami';
  const seeAll = isRtl
    ? 'والعديد من الجامعات الأخرى حول العالم'
    : 'Lihat Semua Universitas →';

  return (
    <section className="py-12 bg-white border-t border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-black text-gray-900">{title}</h2>
          {!isRtl && (
            <a href="#" className="text-yellow font-semibold text-sm hover:underline hidden md:block">{seeAll}</a>
          )}
        </div>

        {/* Logos row */}
        <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
          {LOGOS.map((logo) => (
            <div key={logo.name} className="flex items-center justify-center h-12 grayscale hover:grayscale-0 transition-all duration-300 opacity-70 hover:opacity-100">
              <span
                className="font-black text-sm text-center leading-tight"
                style={{ color: logo.color }}
              >
                {logo.name}
              </span>
            </div>
          ))}
        </div>

        {isRtl && (
          <p className="mt-8 text-center text-sm text-gray-500 font-medium">{seeAll}</p>
        )}
      </div>
    </section>
  );
}
