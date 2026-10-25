import { createServerClient } from "@/lib/supabase/server";
import { notFound } from "next/navigation";
import BlogForm from "@/components/dashboard/BlogForm";

export const dynamic = "force-dynamic";

export default async function EditBlogPostPage(props: { params: Promise<{ slug: string }> }) {
  const params = await props.params;
  const { slug } = params;
  const isNew = slug === "new";

  const supabase = await createServerClient();

  let post = null;
  if (!isNew) {
    let decodedSlug = slug;
    try {
      decodedSlug = decodeURIComponent(slug);
    } catch {
      decodedSlug = slug;
    }

    const { data: directData } = await supabase
      .from("blog_posts")
      .select("*")
      .eq("slug", decodedSlug)
      .maybeSingle();

    if (directData) {
      post = directData;
    } else {
      const { data: fallbackData } = await supabase
        .from("blog_posts")
        .select("*")
        .or(`slug.eq.${slug},id.eq.${slug}`)
        .maybeSingle();

      if (!fallbackData) notFound();
      post = fallbackData;
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-[#1B2A4A]">
        {isNew ? "كتابة مقال جديد" : "تعديل المقال"}
      </h1>
      
      <div className="bg-white p-6 rounded-xl shadow-sm border border-[#E2E8F0]">
        <BlogForm post={post} />
      </div>
    </div>
  );
}
