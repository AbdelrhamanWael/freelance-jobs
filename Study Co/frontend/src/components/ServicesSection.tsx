'use client';

import { useTranslation } from 'react-i18next';
import { MessageCircle } from 'lucide-react';
import { motion } from 'framer-motion';

type ServiceCard = {
  id: string;
  icon: string;
  iconBg: string;
  btnBg: string;
  title: string;
  desc: string;
  img: string;
  imgAlt: string;
};

export default function ServicesSection() {
  const { t, i18n } = useTranslation();
  const isRtl = i18n.language === 'ar';

  const services: ServiceCard[] = isRtl
    ? [
        {
          id: 'abroad',
          icon: '🌐',
          iconBg: 'bg-amber-100',
          btnBg: 'bg-yellow',
          title: 'الدراسة في الخارج',
          desc: 'اختر من أفضل الجامعات في استراليا، بريطانيا، كندا وأكثر من 20 دولة.',
          img: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
          imgAlt: 'Kuala Lumpur and Sydney',
        },
        {
          id: 'english',
          icon: '💬',
          iconBg: 'bg-blue-100',
          btnBg: 'bg-blue-600',
          title: 'تعلم اللغة الإنجليزية',
          desc: 'دورات لغة إنجليزية في أفضل المعاهد والمدارس حول العالم بمستويات تبدأ من المبتدئ حتى المتقدم.',
          img: 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=600&q=80',
          imgAlt: 'English class',
        },
        {
          id: 'online',
          icon: '🖥',
          iconBg: 'bg-purple-100',
          btnBg: 'bg-purple-600',
          title: 'الدرجات الجامعية أونلاين',
          desc: 'برامج بكالوريوس، ماجستير وشهادات معتمدة من جامعات عالمية مرموقة بنظام 100% أونلاين.',
          img: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&q=80',
          imgAlt: 'Online learning',
        },
        {
          id: 'student',
          icon: '👤',
          iconBg: 'bg-green-100',
          btnBg: 'bg-green-600',
          title: 'خدمات الطلاب',
          desc: 'دعم شامل في كل خطوة من رحلتك الدراسية من القبول حتى الوصول والاستقرار.',
          img: 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=600&q=80',
          imgAlt: 'Luggage and passport',
        },
      ]
    : [
        {
          id: 'abroad',
          icon: '🌐',
          iconBg: 'bg-amber-100',
          btnBg: 'bg-yellow',
          title: 'Belajar di Luar Negeri',
          desc: 'Kuliah di universitas terbaik di berbagai negara. Pilihan program lengkap untuk masa depanmu.',
          img: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
          imgAlt: 'City skylines',
        },
        {
          id: 'english',
          icon: '💬',
          iconBg: 'bg-blue-100',
          btnBg: 'bg-blue-600',
          title: 'Belajar Bahasa Inggris',
          desc: 'Kursus bahasa Inggris di institusi terbaik di berbagai negara. Tingkatkan kemampuan bahasamu sekarang!',
          img: 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=600&q=80',
          imgAlt: 'English class',
        },
        {
          id: 'online',
          icon: '🖥',
          iconBg: 'bg-purple-100',
          btnBg: 'bg-purple-600',
          title: 'Gelar Online',
          desc: 'Program Sarjana, Magister, MBA & sertifikasi online dari universitas ternama di seluruh dunia.',
          img: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&q=80',
          imgAlt: 'Online learning',
        },
        {
          id: 'student',
          icon: '👤',
          iconBg: 'bg-green-100',
          btnBg: 'bg-green-600',
          title: 'Layanan Mahasiswa',
          desc: 'Dukungan lengkap mulai dari aplikasi, visa, akomodasi, hingga keberangkatan.',
          img: 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=600&q=80',
          imgAlt: 'Travel and passport',
        },
      ];

  const btnLabel = isRtl ? 'تواصل معنا' : 'Konsultasi Gratis';

  return (
    <section id="services" className="py-16 bg-gray-50/70">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {services.map((svc, i) => (
            <motion.div
              key={svc.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              className="bg-white rounded-3xl overflow-hidden shadow-sm hover:shadow-lg transition-all flex flex-col"
            >
              {/* Top: Icon + Title + Desc + Button */}
              <div className="p-6 flex flex-col flex-1">
                {/* Icon circle */}
                <div className={`w-14 h-14 rounded-full ${svc.iconBg} flex items-center justify-center text-2xl mb-4`}>
                  {svc.icon}
                </div>

                <h3 className="text-xl font-black text-gray-900 mb-3 leading-snug">
                  {svc.title}
                </h3>

                <p className="text-gray-500 text-sm leading-relaxed flex-1 mb-5">
                  {svc.desc}
                </p>

                <a
                  href="https://wa.me/1234567890"
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`flex items-center justify-center gap-2 ${svc.btnBg} text-white font-bold text-sm py-2.5 px-4 rounded-xl w-full transition-opacity hover:opacity-90`}
                >
                  <MessageCircle className="w-4 h-4" />
                  {btnLabel}
                </a>
              </div>

              {/* Bottom: Image */}
              <div className="h-48 overflow-hidden">
                <img
                  src={svc.img}
                  alt={svc.imgAlt}
                  className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
