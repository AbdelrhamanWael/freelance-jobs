import { createServerClient } from "@/lib/supabase/server";

export type BlogPost = {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  content: string;
  cover_image: string;
  author: string;
  author_title?: string;
  author_bio?: string;
  tags: string[];
  is_published: boolean;
  published_at: string;
  created_at: string;
};

export async function getRecentBlogs(limit = 3): Promise<BlogPost[]> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from("blog_posts")
      .select("*")
      .eq("is_published", true)
      .order("created_at", { ascending: false })
      .limit(limit);

    if (error || !data) return [];
    return data as BlogPost[];
  } catch {
    return [];
  }
}

export async function getBlogBySlug(slug: string): Promise<BlogPost | null> {
  try {
    const supabase = await createServerClient();
    let decodedSlug = slug;
    try {
      decodedSlug = decodeURIComponent(slug);
    } catch {
      decodedSlug = slug;
    }

    // Try decoded slug first
    const { data: directData, error: directError } = await supabase
      .from("blog_posts")
      .select("*")
      .eq("slug", decodedSlug)
      .eq("is_published", true)
      .maybeSingle();

    if (directData && !directError) {
      return directData as BlogPost;
    }

    // If not found, try raw slug or ID
    const { data: fallbackData } = await supabase
      .from("blog_posts")
      .select("*")
      .or(`slug.eq.${slug},id.eq.${slug}`)
      .eq("is_published", true)
      .maybeSingle();

    if (fallbackData) return fallbackData as BlogPost;
    return null;
  } catch {
    return null;
  }
}

export async function getRelatedBlogs(currentId: string, limit = 3): Promise<BlogPost[]> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from("blog_posts")
      .select("*")
      .eq("is_published", true)
      .neq("id", currentId)
      .order("created_at", { ascending: false })
      .limit(limit);

    if (error || !data) return [];
    return data as BlogPost[];
  } catch {
    return [];
  }
}
