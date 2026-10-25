'use client';

import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { MessageCircle, ArrowRight } from 'lucide-react';

type Destination = {
  id: string;
  flag: string;
  name: string;
  desc: string;
  img: string;
  btnColor: string;
};

const DESTINATIONS_AR: Destination[] = [
  {
    id: 'my', flag: '🇲🇾',
    name: 'ماليزيا',
    desc: 'جامعات ومعاهد مميزة وتكاليف مناسبة',
    img: 'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=600&q=80',
    btnColor: 'bg-yellow',
  },
  {
    id: 'au', flag: '🇦🇺',
    name: 'أستراليا',
    desc: 'تعليم عالمي وفرص عمل مميزة بعد التخرج',
    img: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
    btnColor: 'bg-blue-600',
  },
  {
    id: 'uk', flag: '🇬🇧',
    name: 'المملكة المتحدة',
    desc: 'تجربة تعليمية عريقة في قلب أوروبا',
    img: 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=600&q=80',
    btnColor: 'bg-gray-900',
  },
  {
    id: 'ca', flag: '🇨🇦',
    name: 'كندا',
    desc: 'بيئة آمنة ومتعددة الثقافات وفرص إقامة مميزة',
    img: 'https://images.unsplash.com/photo-1517935706615-2717063c2225?w=600&q=80',
    btnColor: 'bg-red-600',
  },
  {
    id: 'us', flag: '🇺🇸',
    name: 'الولايات المتحدة',
    desc: 'أفضل الجامعات في العالم',
    img: 'https://images.unsplash.com/photo-1485738422979-f5c462d49f74?w=600&q=80',
    btnColor: 'bg-blue-700',
  },
  {
    id: 'nz', flag: '🇳🇿',
    name: 'نيوزيلندا',
    desc: 'جودة حياة عالية وطبيعة خلابة',
    img: 'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=600&q=80',
    btnColor: 'bg-teal-600',
  },
];

const DESTINATIONS_ID: Destination[] = [
  {
    id: 'my', flag: '🇲🇾',
    name: 'Malaysia',
    desc: 'Banyak pilihan universitas dan biaya terjangkau.',
    img: 'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=600&q=80',
    btnColor: 'bg-yellow',
  },
  {
    id: 'au', flag: '🇦🇺',
    name: 'Australia',
    desc: 'Kualitas pendidikan tinggi dan peluang kerja luas.',
    img: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
    btnColor: 'bg-blue-600',
  },
  {
    id: 'uk', flag: '🇬🇧',
    name: 'United Kingdom',
    desc: 'Pendidikan berkualitas dengan sejarah panjang.',
    img: 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=600&q=80',
    btnColor: 'bg-gray-900',
  },
  {
    id: 'ca', flag: '🇨🇦',
    name: 'Canada',
    desc: 'Lingkungan aman dan multiculture.',
    img: 'https://images.unsplash.com/photo-1517935706615-2717063c2225?w=600&q=80',
    btnColor: 'bg-red-600',
  },
  {
    id: 'us', flag: '🇺🇸',
    name: 'United States',
    desc: 'Universitas terbaik dunia dan inovasi terdepan.',
    img: 'https://images.unsplash.com/photo-1485738422979-f5c462d49f74?w=600&q=80',
    btnColor: 'bg-blue-700',
  },
  {
    id: 'nz', flag: '🇳🇿',
    name: 'New Zealand',
    desc: 'Kualitas hidup tinggi dan alam yang indah.',
    img: 'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=600&q=80',
    btnColor: 'bg-teal-600',
  },
];

export default function DestinationsSection() {
  const { i18n } = useTranslation();
  const isRtl = i18n.language === 'ar';
  const destinations = isRtl ? DESTINATIONS_AR : DESTINATIONS_ID;

  const sectionTitle = isRtl ? 'وجهات الدراسة' : 'Destinasi Studi Populer';
  const seeAll = isRtl ? 'أكثر من 20 دولة حول العالم — تواصل معنا لمعرفة المزيد' : 'Lihat Semua Negara →';
  const btnLabel = isRtl ? 'تواصل معنا' : 'Konsultasi Gratis';

  return (
    <section id="destinations" className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <h2 className="text-3xl font-black text-gray-900">{sectionTitle}</h2>
          {!isRtl && (
            <a href="#" className="text-yellow font-semibold text-sm hover:underline hidden md:flex items-center gap-1">
              {seeAll} <ArrowRight className="w-4 h-4" />
            </a>
          )}
        </div>

        {/* Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {destinations.map((dest, i) => (
            <motion.div
              key={dest.id}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.07 }}
              className="flex flex-col rounded-2xl overflow-hidden border border-gray-100 shadow-sm hover:shadow-md transition-all"
            >
              {/* Image with flag */}
              <div className="relative h-32 overflow-hidden">
                <img
                  src={dest.img}
                  alt={dest.name}
                  className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
                />
                {/* Flag badge */}
                <div className="absolute bottom-2 start-2 text-xl bg-white rounded-full w-8 h-8 flex items-center justify-center shadow-md">
                  {dest.flag}
                </div>
              </div>

              {/* Content */}
              <div className="p-3 flex flex-col flex-1 bg-white">
                <h3 className="font-black text-gray-900 text-sm mb-1">{dest.name}</h3>
                <p className="text-gray-500 text-xs leading-snug mb-3 flex-1">{dest.desc}</p>
                <a
                  href="https://wa.me/1234567890"
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`flex items-center justify-center gap-1 ${dest.btnColor} text-white text-xs font-bold py-2 px-3 rounded-lg transition-opacity hover:opacity-90`}
                >
                  <MessageCircle className="w-3 h-3" />
                  {btnLabel}
                </a>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom note */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500 font-medium">
            {isRtl ? seeAll : ''}
          </p>
        </div>

      </div>
    </section>
  );
}
