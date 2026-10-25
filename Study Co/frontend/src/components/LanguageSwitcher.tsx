'use client';

import { useTranslation } from 'react-i18next';
import { useRouter, usePathname } from 'next/navigation';
import { i18nConfig } from '../../i18nConfig';
import { Globe } from 'lucide-react';

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const currentLocale = i18n.language;
  const router = useRouter();
  const currentPathname = usePathname();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLocale = e.target.value;
    
    const days = 30;
    const date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `NEXT_LOCALE=${newLocale};expires=${date.toUTCString()};path=/`;
    
    router.push(currentPathname.replace(`/${currentLocale}`, `/${newLocale}`));
    router.refresh();
  };

  return (
    <div className="flex items-center gap-1 bg-white/50 px-2 py-1 rounded-md">
      <Globe className="w-4 h-4 text-studyco-dark" />
      <select 
        value={currentLocale} 
        onChange={handleChange}
        className="bg-transparent text-sm border-none outline-none cursor-pointer text-studyco-dark hover:text-studyco-yellow font-medium"
      >
        <option value="ar">العربية</option>
        <option value="id">Indonesia</option>
      </select>
    </div>
  );
}
