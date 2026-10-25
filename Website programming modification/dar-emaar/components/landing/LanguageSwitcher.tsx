"use client";

import { useEffect, useState } from "react";
import Cookies from "js-cookie";

export default function LanguageSwitcher() {
  const [currentLang, setCurrentLang] = useState("ar");

  useEffect(() => {
    // Check if google translate cookie exists
    const googTransCookie = Cookies.get("googtrans");
    if (googTransCookie && googTransCookie.includes("/en")) {
      setCurrentLang("en");
      document.documentElement.dir = "ltr";
    } else {
      setCurrentLang("ar");
      document.documentElement.dir = "rtl";
    }
  }, []);

  const switchLanguage = (lang: "ar" | "en") => {
    // Select the hidden google translate combo box
    const select = document.querySelector(".goog-te-combo") as HTMLSelectElement;
    if (select) {
      select.value = lang;
      select.dispatchEvent(new Event("change"));
      setCurrentLang(lang);
      document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    }
  };

  const toggleLanguage = () => {
    if (currentLang === "ar") {
      switchLanguage("en");
    } else {
      switchLanguage("ar");
    }
  };

  return (
    <div className="relative flex items-center">
      {/* Hidden container required by Google Translate script */}
      <div id="google_translate_element" className="hidden"></div>
      
      {/* Custom Button */}
      <button
        onClick={toggleLanguage}
        className="flex items-center gap-2 text-sm font-bold text-[var(--color-primary)] bg-[var(--color-primary)]/5 hover:bg-[var(--color-primary)]/10 px-3 py-1.5 rounded-sm transition-colors border border-[var(--color-primary)]/20 shadow-sm notranslate"
        aria-label="تغيير اللغة"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
        </svg>
        <span className="mt-0.5">{currentLang === "ar" ? "EN" : "عربي"}</span>
      </button>
    </div>
  );
}
