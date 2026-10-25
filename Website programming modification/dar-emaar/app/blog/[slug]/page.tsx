import { redirect, notFound } from "next/navigation";
import { getSettings } from "@/lib/settings";
import { getPageContent } from "@/lib/content";
import { getBlogBySlug, getRelatedBlogs } from "@/lib/db-blogs";
import type { Metadata } from "next";
import Navbar from "@/components/landing/Navbar";
import Footer from "@/components/landing/Footer";
import BlogDetail from "@/components/landing/BlogDetail";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = await getBlogBySlug(slug);

  if (!post) {
    return {
      title: "المقال غير موجود | دار اعمار الغربية",
      description: "المقال المطلوب غير موجود في مدونة دار اعمار الغربية.",
    };
  }

  return {
    title: `${post.title} | دار اعمار الغربية`,
    description: post.excerpt || post.title,
    openGraph: {
      title: post.title,
      description: post.excerpt || post.title,
      images: post.cover_image && !post.cover_image.startsWith("file:") ? [post.cover_image] : [],
    },
  };
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params;

  const settings = await getSettings();
  if (!settings.is_blog_enabled) {
    redirect("/");
  }

  const post = await getBlogBySlug(slug);
  if (!post) {
    notFound();
  }

  const content = await getPageContent();
  const relatedPosts = await getRelatedBlogs(post.id, 3);

  return (
    <>
      <Navbar
        isBlogEnabled={settings.is_blog_enabled}
        headerCtaText={content.header_cta_text}
        logoUrl={settings.logo_url}
      />
      <BlogDetail
        post={post}
        relatedPosts={relatedPosts}
        settings={settings}
      />
      <Footer />
    </>
  );
}
