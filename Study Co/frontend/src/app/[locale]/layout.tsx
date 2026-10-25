import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import { dir } from 'i18next';
import { i18nConfig } from "../../../i18nConfig";

const geist = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "StudyCo Education Services",
  description: "نساعد الطلاب على تحقيق أحلامهم الدراسية من خلال الجامعات والمعاهد والبرامج العالمية الموثوقة.",
};

export function generateStaticParams() {
  return i18nConfig.locales.map((locale) => ({ locale }));
}

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  return (
    <html
      lang={locale}
      dir={dir(locale)}
      className={`${geist.variable}`}
    >
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body className="min-h-screen bg-white">{children}</body>
    </html>
  );
}
