"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import type { DbCategory } from "@/lib/db-projects";
import { Grip, Building2, Paintbrush, Zap, Home, Wrench, FolderOpen } from "lucide-react";

const getCategoryIcon = (slug: string) => {
  switch (slug) {
    case "all": return <Grip className="w-4 h-4" />;
    case "design-build": return <Building2 className="w-4 h-4" />;
    case "finishing": return <Paintbrush className="w-4 h-4" />;
    case "infrastructure": return <Wrench className="w-4 h-4" />;
    case "electromechanical": return <Zap className="w-4 h-4" />;
    case "residential": return <Home className="w-4 h-4" />;
    default: return <FolderOpen className="w-4 h-4" />;
  }
};

type Props = {
  categories: DbCategory[];
  activeCategory: string;
  totalCount: number;
};

export default function CategoryFilter({ categories, activeCategory, totalCount }: Props) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const handleFilter = (slug: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (slug === "all") {
      params.delete("category");
    } else {
      params.set("category", slug);
    }
    router.push(`/projects?${params.toString()}`, { scroll: false });
  };

  const tabs = [
    { slug: "all", name: "الكل" },
    ...categories,
  ];

  return (
    <div className="flex flex-wrap gap-2 justify-center sm:justify-start">
      {tabs.map((tab) => {
        const isActive = tab.slug === activeCategory;
        return (
          <button
            key={tab.slug}
            onClick={() => handleFilter(tab.slug)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-sm text-sm font-semibold transition-all duration-200 border ${
              isActive
                ? "text-white border-transparent shadow-md"
                : "bg-white border-[#E2E8F0] hover:border-[#004B4B]/30 hover:shadow-sm"
            }`}
            style={
              isActive
                ? { background: "var(--color-primary, #004B4B)", color: "white" }
                : { color: "var(--color-accent, #6C6D71)" }
            }
            aria-current={isActive ? "page" : undefined}
          >
            <span className="flex-shrink-0">
              {getCategoryIcon(tab.slug)}
            </span>
            {tab.name}
            {tab.slug === "all" && (
              <span
                className={`text-xs px-1.5 py-0.5 rounded-full font-mono ${
                  isActive ? "bg-white/20" : "bg-[#F1F5F9]"
                }`}
              >
                {totalCount}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
