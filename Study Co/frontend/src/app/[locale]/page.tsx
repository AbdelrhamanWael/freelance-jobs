import initTranslations from '@/i18n';
import TranslationProvider from '@/components/TranslationProvider';
import Navbar from '@/components/Navbar';
import HeroSection from '@/components/HeroSection';
import ServicesSection from '@/components/ServicesSection';
import DestinationsSection from '@/components/DestinationsSection';
import StatsSection from '@/components/StatsSection';
import TestimonialsSection from '@/components/TestimonialsSection';
import PartnersSection from '@/components/PartnersSection';
import Footer from '@/components/Footer';

const i18nNamespaces = ['common'];

export default async function Home({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const { resources } = await initTranslations(locale, i18nNamespaces);

  return (
    <TranslationProvider
      locale={locale}
      namespaces={i18nNamespaces}
      resources={resources}
    >
      <Navbar />
      <main className="flex-1 w-full overflow-x-hidden">
        <HeroSection />
        <ServicesSection />
        <DestinationsSection />
        <StatsSection />
        <TestimonialsSection />
        <PartnersSection />
      </main>
      <Footer />
    </TranslationProvider>
  );
}
