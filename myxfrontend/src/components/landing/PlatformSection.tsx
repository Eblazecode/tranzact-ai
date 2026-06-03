import { useState } from "react";
import { BarChart3, Brain, TrendingUp } from "lucide-react";
import dashboardMockup from "@/assets/dashboard-mockup.jpg";
import predictionsMockup from "@/assets/predictions-mockup.jpg";

const tabs = [
  {
    id: "insights",
    label: "Spending Insights",
    icon: BarChart3,
    title: "11 insight modules. One clear picture.",
    description:
      "From category breakdowns and spending patterns to anomaly detection and financial leakage — TransacAI gives you the complete story behind every naira.",
    image: dashboardMockup,
  },
  {
    id: "predictions",
    label: "AI Predictions",
    icon: Brain,
    title: "Know what's coming before it arrives.",
    description:
      "Our Gradient Boosting model predicts your next month's spending with SHAP-powered explanations in plain English. No data science degree needed.",
    image: predictionsMockup,
  },
  {
    id: "recommendations",
    label: "Smart Recommendations",
    icon: TrendingUp,
    title: "6 personalised actions. Real impact.",
    description:
      "From savings strategies to leakage alerts, TransacAI generates tailored recommendations ranked by how much money they could save you.",
    image: dashboardMockup,
  },
];

export function PlatformSection() {
  const [activeTab, setActiveTab] = useState("insights");
  const active = tabs.find((t) => t.id === activeTab) ?? tabs[0];

  return (
    <section className="py-24 bg-muted/30">
      <div className="mx-auto max-w-7xl px-4">
        <div className="text-center mb-12">
          <p className="text-sm font-semibold uppercase tracking-widest text-primary mb-3">
            The TransacAI Platform
          </p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-4">
            Connected insights make smarter decisions easy
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
            Upload once. Get analytics, predictions, and recommendations — all working together.
          </p>
        </div>

        {/* Tab switcher */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-12">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-5 py-3 rounded-full text-sm font-medium transition-all duration-300 ${
                activeTab === tab.id
                  ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
                  : "bg-card border border-border text-muted-foreground hover:text-foreground hover:border-primary/30"
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content area */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="order-2 lg:order-1">
            <h3 className="text-2xl sm:text-3xl font-bold text-foreground mb-4">
              {active.title}
            </h3>
            <p className="text-muted-foreground text-lg leading-relaxed mb-8">
              {active.description}
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <a
                href="#get-started"
                className="inline-flex items-center gap-2 text-primary font-semibold hover:underline"
              >
                Get started free →
              </a>
              <a
                href="#how-it-works"
                className="inline-flex items-center gap-2 text-muted-foreground font-medium hover:text-foreground"
              >
                See how it works
              </a>
            </div>
          </div>
          <div className="order-1 lg:order-2">
            <div className="rounded-2xl overflow-hidden shadow-2xl ring-1 ring-border bg-card">
              <img
                src={active.image}
                alt={active.label}
                className="w-full h-auto"
                loading="lazy"
                width={1280}
                height={800}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
