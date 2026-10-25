import type { Metadata } from "next";
import type { CSSProperties } from "react";
import { Analytics } from "@vercel/analytics/react";
import { GoogleAnalytics } from "@next/third-parties/google";
import { Tajawal } from "next/font/google";
import Script from "next/script";
import { getSettings } from "@/lib/settings";
import "./globals.css";

const tajawal = Tajawal({
  subsets: ["arabic", "latin"],
  weight: ["300", "400", "500", "700", "800", "900"],
  display: "swap",
  variable: "--font-brand",
});

export const metadata: Metadata = {
  title: "دار اعمار الغربية | مقاولات عامة - تصميم وبناء وتشطيب",
  description:
    "شركة دار اعمار الغربية للمقاولات العامة. خبرة أكثر من 15 عاماً في التصميم والبناء والتشطيبات الداخلية وإدارة المشاريع. احصل على عرض سعر مجاني اليوم.",
  keywords:
    "مقاولات, بناء, تشطيبات, دار اعمار الغربية, تصميم معماري, إدارة مشاريع",
  openGraph: {
    title: "دار اعمار الغربية | مقاولات عامة",
    description:
      "خبرة أكثر من 15 عاماً في البناء والتشطيبات. احصل على عرض سعر مجاني.",
    locale: "ar_SA",
    type: "website",
  },
  verification: {
    google: "FmvV7oGZ1tC26FSQqFqaxn4R6bAZZ5O5Gw-l6L-9vAw",
  },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Fetch brand colors from Supabase (cached 60s, revalidates on settings save)
  const settings = await getSettings();

  // Inject brand colors as CSS custom properties on the root element.
  // This is the ONLY safe way to use dynamic colors with Tailwind v4 —
  const fontBaseSize =
    settings.font_scale === "large" ? "18px" :
    settings.font_scale === "medium" ? "17px" : "16px";

  const cssVars = {
    "--color-primary": settings.primary_color,
    "--color-secondary": settings.secondary_color,
    "--color-accent": settings.accent_color,
    "--font-base-size": fontBaseSize,
  } as CSSProperties;

  const gaId = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID || "G-LD9138VZSC";

  return (
    <html lang="ar" dir="rtl" className={tajawal.variable} style={cssVars}>
      <head />
      <body className="font-sans">
        {children}
        <Analytics />
        {gaId && <GoogleAnalytics gaId={gaId} />}
        <Script
          src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"
          strategy="afterInteractive"
        />
        <Script id="google-translate-init" strategy="afterInteractive">
          {`
            function googleTranslateElementInit() {
              new window.google.translate.TranslateElement({
                pageLanguage: 'ar',
                includedLanguages: 'ar,en',
                autoDisplay: false
              }, 'google_translate_element');
            }
          `}
        </Script>
      </body>
    </html>
  );
}
