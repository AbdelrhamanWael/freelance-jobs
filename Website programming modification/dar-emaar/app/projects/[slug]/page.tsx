import { notFound } from "next/navigation";
import { getDbProjectBySlug, getDbProjects } from "@/lib/db-projects";
import { getPageContent } from "@/lib/content";
import type { Metadata } from "next";
import ProjectDetail from "@/components/landing/ProjectDetail";
import Navbar from "@/components/landing/Navbar";
import Footer from "@/components/landing/Footer";
import { getSettings } from "@/lib/settings";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const project = await getDbProjectBySlug(slug);
  if (!project) return { title: "المشروع غير موجود" };
  return {
    title: `${project.title} | دار اعمار الغربية`,
    description: project.description || "تفاصيل المشروع",
  };
}

export default async function ProjectPage({ params }: Props) {
  const { slug } = await params;
  const project = await getDbProjectBySlug(slug);
  const content = await getPageContent();
  const settings = await getSettings();

  if (!project) notFound();

  return (
    <>
      <Navbar isBlogEnabled={settings.is_blog_enabled} headerCtaText={content.header_cta_text} logoUrl={settings.logo_url} />
      <ProjectDetail project={project} content={content} />
      <Footer />
    </>
  );
}

