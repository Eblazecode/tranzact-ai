import { Upload, Cpu, LayoutDashboard, CheckCircle } from "lucide-react";
import dashboardMockup from "@/assets/dashboard-mockup.jpg";

const steps = [
  {
    icon: Upload,
    number: "1",
    title: "Select your bank & upload",
    description:
      "Choose from GTBank, OPay, Moniepoint, Zenith Bank, or Ecobank. Then drag and drop your original statement file.",
  },
  {
    icon: Cpu,
    number: "2",
    title: "AI cleans & analyses",
    description:
      "Our bank-specific processors structure your data. Then AI runs spending analysis, predictions, and recommendations.",
  },
  {
    icon: LayoutDashboard,
    number: "3",
    title: "Explore your dashboard",
    description:
      "Get a complete financial picture — 11 insight modules, predictive analytics, health scores, and personalised advice.",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-24 bg-background">
      <div className="mx-auto max-w-7xl px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left: Steps */}
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-primary mb-3">
              Simple & Fast
            </p>
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
              From raw statement to full intelligence in 60 seconds
            </h2>
            <p className="text-muted-foreground text-lg mb-10">
              Three steps. Zero complexity. Just upload and understand.
            </p>

            <div className="space-y-8">
              {steps.map((step, i) => (
                <div key={step.number} className="flex gap-5">
                  <div className="flex flex-col items-center">
                    <div className="h-12 w-12 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold text-lg shrink-0">
                      {step.number}
                    </div>
                    {i < steps.length - 1 && (
                      <div className="w-0.5 flex-1 bg-border mt-2" />
                    )}
                  </div>
                  <div className="pb-8">
                    <h3 className="text-xl font-semibold text-foreground mb-2">
                      {step.title}
                    </h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-3 mt-4 p-4 rounded-xl bg-primary/5 border border-primary/10">
              <CheckCircle className="h-5 w-5 text-primary shrink-0" />
              <p className="text-sm text-foreground">
                <strong>Result:</strong> A professional dashboard with 11+ insight modules, AI predictions, and 6 personalised recommendations.
              </p>
            </div>
          </div>

          {/* Right: Dashboard mockup */}
          <div className="relative">
            <div className="rounded-2xl overflow-hidden shadow-2xl ring-1 ring-border">
              <img
                src={dashboardMockup}
                alt="TransacAI dashboard preview showing spending analytics and charts"
                className="w-full h-auto"
                loading="lazy"
                width={1280}
                height={800}
              />
            </div>
            {/* Floating stat cards */}
            <div className="absolute -bottom-6 -left-4 bg-card rounded-xl shadow-lg border border-border p-4 animate-fade-up">
              <p className="text-xs text-muted-foreground">Processing time</p>
              <p className="text-2xl font-bold text-primary">&lt; 60s</p>
            </div>
            <div className="absolute -top-4 -right-4 bg-card rounded-xl shadow-lg border border-border p-4 animate-fade-up" style={{ animationDelay: "0.2s" }}>
              <p className="text-xs text-muted-foreground">Insight modules</p>
              <p className="text-2xl font-bold text-primary">11+</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
