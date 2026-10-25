'use client';

import { I18nextProvider } from 'react-i18next';
import { createInstance } from 'i18next';
import initTranslations from '@/i18n';
import { ReactNode, useMemo, useEffect, useState } from 'react';

export default function TranslationProvider({
  children,
  locale,
  namespaces,
  resources
}: {
  children: ReactNode;
  locale: string;
  namespaces: string[];
  resources: any;
}) {
  const [i18nInstance, setI18nInstance] = useState(() => {
    const instance = createInstance();
    initTranslations(locale, namespaces, instance, resources);
    return instance;
  });

  return <I18nextProvider i18n={i18nInstance}>{children}</I18nextProvider>;
}
