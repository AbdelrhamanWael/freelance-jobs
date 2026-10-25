import Navbar from "@/components/landing/Navbar";
import Hero from "@/components/landing/Hero";
import TrustBar from "@/components/landing/TrustBar";
import Services from "@/components/landing/Services";
import FeaturedProject from "@/components/landing/FeaturedProject";
import ClientLogos from "@/components/landing/ClientLogos";
import LeadForm from "@/components/landing/LeadForm";
import Footer from "@/components/landing/Footer";
import RecentBlogs from "@/components/landing/RecentBlogs";

import { getPageContent, getContactServices } from "@/lib/content";
import { getSettings } from "@/lib/settings";
import { getDbProjects } from "@/lib/db-projects";
import { getDbClients } from "@/lib/db-clients";
import { getStats } from "@/app/actions/stats";

export default async function Home() {
  const content = await getPageContent();
  const settings = await getSettings();
  const contactServices = getContactServices(content);
  
  // Fetch only featured projects for the home page, fallback to first 6 if none featured
  const allProjects = await getDbProjects();
  let featuredProjects = allProjects.filter(p => p.is_featured);
  
  if (featuredProjects.length === 0) {
    featuredProjects = allProjects.slice(0, 7); // Fallback so section doesn't disappear
  }

  const clients = await getDbClients();
  const stats = await getStats();

  return (
    <>
      <Navbar 
        isBlogEnabled={settings.is_blog_enabled} 
        headerCtaText={content.header_cta_text}
        logoUrl={settings.logo_url}
      />
      <main>
        <Hero content={content} heroBgImage={settings.hero_bg_image} />
        {content.trust_enabled !== "false" && stats.length > 0 && <TrustBar stats={stats} />}
        <Services content={content} />
        <FeaturedProject projects={featuredProjects} content={content} />
        <ClientLogos dbClients={clients} />
        <LeadForm services={contactServices} />
      </main>
      <Footer />
    </>
  );
}
