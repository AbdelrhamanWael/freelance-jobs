/**
 * lib/db-projects.ts
 * Database-backed project and category fetching from Supabase.
 * Falls back gracefully to empty arrays if DB is unavailable.
 */

import { createServerClient } from "@/lib/supabase/server";

export type DbCategory = {
  id: string;
  name: string;
  slug: string;
  icon: string | null;
  sort_order: number;
};

export type DbProject = {
  id: string;
  slug: string;
  title: string;
  category_id: string | null;
  category?: DbCategory | null;
  location: string | null;
  client: string | null;
  duration: string | null;
  area: string | null;
  floors: string | null;
  year: string | null;
  description: string | null;
  scope: string[] | null;
  images: string[] | null;
  thumbnail_index: number;
  attachment_file: string | null;
  attachment_label: string | null;
  is_featured: boolean;
  is_published: boolean;
  sort_order: number;
};

export async function getDbProjects(categorySlug?: string): Promise<DbProject[]> {
  try {
    const supabase = await createServerClient();
    let query = supabase
      .from("projects")
      .select("*, category:categories(id, name, slug, icon, sort_order)")
      .eq("is_published", true)
      .order("sort_order", { ascending: true });

    if (categorySlug && categorySlug !== "all") {
      let decodedCatSlug = categorySlug;
      try {
        decodedCatSlug = decodeURIComponent(categorySlug);
      } catch {}
      // Filter by category slug via join
      query = query.eq("categories.slug", decodedCatSlug);
    }

    const { data, error } = await query;

    if (error) {
      console.warn("[db-projects] Error fetching projects:", error.message);
      return [];
    }

    return (data || []) as DbProject[];
  } catch {
    return [];
  }
}

/** Fetch a single project by slug or ID, supporting decoded Arabic slugs. */
export async function getDbProjectBySlug(slug: string): Promise<DbProject | null> {
  try {
    const supabase = await createServerClient();
    let decodedSlug = slug;
    try {
      decodedSlug = decodeURIComponent(slug);
    } catch {
      decodedSlug = slug;
    }

    // 1. Try decoded slug first
    let { data } = await supabase
      .from("projects")
      .select("*, category:categories(id, name, slug, icon, sort_order)")
      .eq("slug", decodedSlug)
      .eq("is_published", true)
      .maybeSingle();

    // 2. If not found and slug differed from decodedSlug, try raw slug
    if (!data && decodedSlug !== slug) {
      const res = await supabase
        .from("projects")
        .select("*, category:categories(id, name, slug, icon, sort_order)")
        .eq("slug", slug)
        .eq("is_published", true)
        .maybeSingle();
      data = res.data;
    }

    // 3. If still not found, try matching by UUID id
    if (!data) {
      const resById = await supabase
        .from("projects")
        .select("*, category:categories(id, name, slug, icon, sort_order)")
        .eq("id", slug)
        .eq("is_published", true)
        .maybeSingle();
      data = resById.data;
    }

    if (!data) return null;
    return data as DbProject;
  } catch (err) {
    console.error("[getDbProjectBySlug] Error fetching project:", err);
    return null;
  }
}

export async function getDbCategories(): Promise<DbCategory[]> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from("categories")
      .select("id, name, slug, icon, sort_order")
      .order("sort_order", { ascending: true });

    if (error || !data) return [];
    return data as DbCategory[];
  } catch {
    return [];
  }
}
