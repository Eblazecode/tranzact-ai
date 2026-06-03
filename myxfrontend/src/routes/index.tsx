import { createFileRoute } from "@tanstack/react-router";
import { Navbar } from "@/components/landing/Navbar";
import { HeroSection } from "@/components/landing/HeroSection";
import { TrustBar } from "@/components/landing/TrustBar";
import { PlatformSection } from "@/components/landing/PlatformSection";
import { FeaturesSection } from "@/components/landing/FeaturesSection";
import { HowItWorksSection } from "@/components/landing/HowItWorksSection";
import { StatsSection } from "@/components/landing/StatsSection";
import { ShowcaseSection } from "@/components/landing/ShowcaseSection";
import { ProductCardsSection } from "@/components/landing/ProductCardsSection";
import { CTASection } from "@/components/landing/CTASection";
import { Footer } from "@/components/landing/Footer";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "TransacAI — Turn Your Bank Statement Into Financial Intelligence" },
      {
        name: "description",
        content:
          "Upload your Nigerian bank statement and get AI-powered spending insights, predictions, and recommendations in under 60 seconds. Supports OPay, Moniepoint, Zenith, GTBank, and Ecobank.",
      },
      { property: "og:title", content: "TransacAI — Financial Intelligence for Nigeria" },
      {
        property: "og:description",
        content:
          "AI-powered analytics for your bank statements. Deep insights, predictions, and personalised recommendations.",
      },
      { property: "og:type", content: "website" },
    ],
  }),
  component: LandingPage,
});

function LandingPage() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <HeroSection />
      <TrustBar />
      <PlatformSection />
      <FeaturesSection />
      <HowItWorksSection />
      <StatsSection />
      <ShowcaseSection />
      <ProductCardsSection />
      <CTASection />
      <Footer />
    </div>
  );
}
