'use client';

import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import { useState } from 'react';

type Testimonial = {
  name: string;
  university: string;
  text: string;
  avatar: string;
};

const TESTIMONIALS_AR: Testimonial[] = [
  {
    name: 'فخري رمضان',
    university: 'جامعة Sunway، ماليزيا',
    text: 'ساعدتني StudyCo في الحصول على قبول جامعي في ماليزيا بسهولة. وبدون أي تعقيدات.',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80',
  },
  {
    name: 'سارة عائشة',
    university: 'جامعة Monash، أستراليا',
    text: 'فريق StudyCo كان متعاون جداً من أول استشارة حتى وصولي إلى أستراليا. شكراً لكم!',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&q=80',
  },
  {
    name: 'ديمصن براسيتيو',
    university: 'MBA Online، المملكة المتحدة',
    text: 'برنامجهم مرن ومعلوماتهم دقيقة، الآن أدرس الماجستير أونلاين في جامعة بريطانية.',
    avatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=100&q=80',
  },
];

const TESTIMONIALS_ID: Testimonial[] = [
  {
    name: 'Fahri Ramadhan',
    university: 'Sunway University, Malaysia',
    text: 'StudyCo sangat membantu saya mendapatkan beasiswa di Malaysia. Prosesnya cepat dan mudah!',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80',
  },
  {
    name: 'Siti Aulia',
    university: 'Monash University, Australia',
    text: 'Tim StudyCo selalu siap membantu dari awal sampai saya berangkat ke Australia. Terima kasih StudyCo!',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&q=80',
  },
  {
    name: 'Dimas Prasetyo',
    university: 'MBA Online, UK',
    text: 'Program online-nya fleksibel dan berkualitas. Sekarang saya bisa kuliah sambil bekerja.',
    avatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=100&q=80',
  },
];

export default function TestimonialsSection() {
  const { i18n } = useTranslation();
  const isRtl = i18n.language === 'ar';
  const testimonials = isRtl ? TESTIMONIALS_AR : TESTIMONIALS_ID;

  const title = isRtl ? 'ماذا يقول طلابنا؟' : 'Apa kata mereka?';
  const seeAll = isRtl ? '' : 'Lihat Semua Testimoni →';

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <h2 className="text-3xl font-black text-gray-900">{title}</h2>
          {!isRtl && (
            <a href="#" className="text-yellow font-semibold text-sm hover:underline hidden md:block">{seeAll}</a>
          )}
        </div>

        {/* Testimonials grid - 3 columns on desktop, same layout as design */}
        <div className="grid md:grid-cols-3 gap-6 relative">
          {/* Prev arrow */}
          <button className="absolute -start-8 top-1/2 -translate-y-1/2 w-8 h-8 bg-white border border-gray-200 rounded-full shadow flex items-center justify-center hover:bg-gray-50 transition z-10 hidden lg:flex">
            {isRtl ? <ArrowRight className="w-4 h-4 text-gray-500" /> : <ArrowLeft className="w-4 h-4 text-gray-500" />}
          </button>

          {testimonials.map((t, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all"
            >
              {/* Text */}
              <p className="text-gray-700 text-sm leading-relaxed mb-6">
                {t.text}
              </p>

              {/* Author */}
              <div className="flex items-center gap-3">
                <img
                  src={t.avatar}
                  alt={t.name}
                  className="w-12 h-12 rounded-full object-cover border-2 border-white shadow"
                />
                <div>
                  <p className="font-bold text-gray-900 text-sm">{t.name}</p>
                  <p className="text-xs text-gray-500">{t.university}</p>
                  <div className="flex gap-0.5 text-yellow text-sm mt-0.5">
                    ★★★★★
                  </div>
                </div>
              </div>
            </motion.div>
          ))}

          {/* Next arrow */}
          <button className="absolute -end-8 top-1/2 -translate-y-1/2 w-8 h-8 bg-white border border-gray-200 rounded-full shadow flex items-center justify-center hover:bg-gray-50 transition z-10 hidden lg:flex">
            {isRtl ? <ArrowLeft className="w-4 h-4 text-gray-500" /> : <ArrowRight className="w-4 h-4 text-gray-500" />}
          </button>
        </div>

      </div>
    </section>
  );
}
