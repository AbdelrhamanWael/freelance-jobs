'use client';

import { useTranslation } from 'react-i18next';
import { MessageCircle } from 'lucide-react';
import Link from 'next/link';

export default function Footer() {
  const { i18n } = useTranslation();
  const isRtl = i18n.language === 'ar';

  const columns = isRtl ? {
    col1: {
      title: 'الدراسة في الخارج',
      links: ['ماليزيا', 'أستراليا', 'المملكة المتحدة', 'كندا', 'الولايات المتحدة', 'دول أخرى'],
    },
    col2: {
      title: 'تعلم الإنجليزية',
      links: ['دورات عامة', 'دورات أكاديمية', 'دورات تجارية', 'دورات أونلاين'],
    },
    col3: {
      title: 'الدرجات الجامعية أونلاين',
      links: ['برامج البكالوريوس', 'برامج الماجستير', 'الشهادات', 'برامج المهنية', 'الدرجات المشتركة'],
    },
    col4: {
      title: 'خدمات الطلاب',
      links: ['القبول والتسجيل', 'إجراءات التأشيرة', 'الإقامة والسكن', 'دعم وثائق', 'الاستقبال من المطار', 'المساعدة الطلابية'],
    },
    col5: {
      title: 'عنا',
      links: ['من نحن', 'فريق العمل', 'تم كاري', 'مقالات وأخبار', 'الشركاء والأكاديميون'],
    },
  } : {
    col1: {
      title: 'Belajar di Luar Negeri',
      links: ['Malaysia', 'Australia', 'United States', 'Canada', 'United Kingdom', 'Negara Lainnya'],
    },
    col2: {
      title: 'Belajar Bahasa Inggris',
      links: ['Malaysia', 'Australia', 'United Kingdom', 'Canada', 'United States', 'Negara Lainnya'],
    },
    col3: {
      title: 'Gelar Online',
      links: ['Program Sarjana', 'Program Magister', 'MBA Online', 'Sertifikasi', 'Program Singkat'],
    },
    col4: {
      title: 'Layanan Mahasiswa',
      links: ['Konsultasi Visa', 'Akomodasi', 'Penjemputan Bandara', 'Asuransi', 'Terjemahan Dokumen', 'Dukungan Mahasiswa'],
    },
    col5: {
      title: 'Tentang Kami',
      links: ['Tentang StudyCo', 'Tim Kami', 'Karir', 'Artikel & Blog', 'Hubungi Kami'],
    },
  };

  const ctaTitle = isRtl ? 'جاهز لبدء رحلتك التعليمية؟' : 'Siap Memulai Perjalanan Pendidikan Anda?';
  const ctaSubtitle = isRtl
    ? 'تواصل معنا الآن واحصل على استشارة مجانية من خبرائنا.'
    : 'Konsultasi gratis bersama tim ahli StudyCo sekarang.';
  const ctaBtn = isRtl ? 'تواصل معنا الآن عبر واتساب' : 'Konsultasi Gratis di WhatsApp';
  const aboutText = isRtl
    ? 'StudyCo هي خدمة تعليمية دولية تكرس جهودها لمساعدة الطلاب الإندونيسيين على تحقيق أحلامهم التعليمية حول العالم.'
    : 'StudyCo adalah layanan pendidikan internasional yang berkomitmen membantu pelajar Indonesia meraih masa depan global yang lebih baik.';
  const copyright = isRtl
    ? '© 2024 StudyCo Education Services. جميع الحقوق محفوظة.'
    : 'Kebijakan Privasi | Syarat & Ketentuan';

  return (
    <footer className="bg-[#111827] text-white">

      {/* CTA Banner */}
      <div className="bg-yellow py-10 px-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            {/* Headphone icon */}
            <div className="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center text-3xl flex-shrink-0">
              🎧
            </div>
            <div>
              <h2 className="text-xl font-black text-gray-900">{ctaTitle}</h2>
              <p className="text-gray-800/80 text-sm font-medium">{ctaSubtitle}</p>
            </div>
          </div>
          <a
            href="https://wa.me/1234567890"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-gray-900 hover:bg-black text-white font-bold px-6 py-3.5 rounded-full transition-all hover:scale-105 whitespace-nowrap shadow-lg"
          >
            <MessageCircle className="w-5 h-5" />
            {ctaBtn}
          </a>
        </div>
      </div>

      {/* Footer Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">

          {/* Brand column */}
          <div className="col-span-2 lg:col-span-1">
            <div className="flex flex-col mb-4">
              <span className="text-xl font-extrabold text-white">StudyCo</span>
              <span className="text-[8px] font-semibold tracking-[2px] text-gray-400 uppercase">Education Services</span>
            </div>
            <p className="text-gray-400 text-xs leading-relaxed mb-5">{aboutText}</p>
            {/* Social icons */}
            <div className="flex gap-3">
              {['📷', '📘', '▶', '🎵'].map((icon, i) => (
                <a key={i} href="#" className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-sm hover:bg-yellow/20 transition-colors">
                  {icon}
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(columns).map(([key, col]) => (
            <div key={key}>
              <h4 className="font-bold text-white text-sm mb-4">{col.title}</h4>
              <ul className="space-y-3">
                {col.links.map((link) => (
                  <li key={link}>
                    <a href="#" className="text-gray-400 text-xs hover:text-yellow transition-colors">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-6 border-t border-white/10 flex flex-col md:flex-row items-center justify-between gap-3">
          <p className="text-gray-500 text-xs">
            {isRtl
              ? copyright
              : '© 2024 StudyCo Education Services. جميع الحقوق محفوظة.'}
          </p>
          {!isRtl && (
            <p className="text-gray-500 text-xs">{copyright}</p>
          )}
        </div>
      </div>
    </footer>
  );
}
