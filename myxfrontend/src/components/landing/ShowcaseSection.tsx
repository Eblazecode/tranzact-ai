import { useEffect, useRef, useState } from "react";
import { BarChart3, Brain, Lightbulb, TrendingUp, PieChart } from "lucide-react";

const features = [
  { icon: BarChart3, title: "11 Spending Insights", desc: "Deep analytics from every single transaction in your statement" },
  { icon: Brain, title: "AI-Powered Predictions", desc: "Know what you will spend before the month even starts" },
  { icon: TrendingUp, title: "Explainable AI Charts", desc: "Understand exactly why the AI made each prediction" },
  { icon: Lightbulb, title: "Personalised Recommendations", desc: "Actionable steps to improve your financial health" },
  { icon: PieChart, title: "Category Breakdowns", desc: "See where every naira goes with interactive charts" },
];

function MiniDashboard() {
  return (
    <div className="bg-card border border-border rounded-2xl shadow-2xl p-4 w-[340px] sm:w-[400px] animate-float">
      {/* Mini sidebar hint */}
      <div className="flex gap-3 mb-3">
        <div className="w-[80px] bg-sidebar rounded-lg p-2 space-y-1.5">
          <div className="h-2 w-10 bg-primary/30 rounded" />
          <div className="h-2 w-12 bg-sidebar-accent rounded" />
          <div className="h-2 w-8 bg-sidebar-accent rounded" />
          <div className="h-2 w-10 bg-sidebar-accent rounded" />
        </div>
        <div className="flex-1">
          <p className="text-[10px] text-muted-foreground">Good Morning,</p>
          <p className="text-xs font-bold text-card-foreground">Oluwapelumi</p>
          {/* Mini stat cards */}
          <div className="grid grid-cols-2 gap-1.5 mt-2">
            <div className="bg-background border border-border rounded-md p-1.5">
              <p className="text-[8px] text-muted-foreground">Total Balance</p>
              <p className="text-[10px] font-bold text-card-foreground">N2,847,500</p>
            </div>
            <div className="bg-background border border-border rounded-md p-1.5">
              <p className="text-[8px] text-muted-foreground">Net Position</p>
              <p className="text-[10px] font-bold text-card-foreground">+N340,200</p>
            </div>
          </div>
          {/* Mini bar chart */}
          <div className="mt-2 flex items-end gap-1 h-[40px]">
            {[65, 80, 95, 70, 55, 75].map((h, i) => (
              <div key={i} className="flex gap-0.5 flex-1">
                <div className="flex-1 rounded-t-sm" style={{ height: `${h * 0.4}px`, backgroundColor: "var(--chart-1)" }} />
                <div className="flex-1 rounded-t-sm" style={{ height: `${h * 0.3}px`, backgroundColor: "var(--chart-3)" }} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function ShowcaseSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setVisible(true); },
      { threshold: 0.15 }
    );
    if (sectionRef.current) obs.observe(sectionRef.current);
    return () => obs.disconnect();
  }, []);

  return (
    <section ref={sectionRef} className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 hero-gradient opacity-30" />
      <div className="relative z-10 mx-auto max-w-7xl px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-4">
            Everything you need to understand your money
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload your bank statement and get a complete financial picture — instantly
          </p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left: Mini Dashboard */}
          <div className={`flex justify-center transition-all duration-700 ${visible ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-12"}`}>
            <MiniDashboard />
          </div>
          {/* Right: Feature highlights */}
          <div className="space-y-6">
            {features.map((f, i) => (
              <div
                key={f.title}
                className={`flex items-start gap-4 transition-all duration-500 ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}`}
                style={{ transitionDelay: visible ? `${i * 120}ms` : "0ms" }}
              >
                <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-primary/15 flex items-center justify-center">
                  <f.icon className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-foreground">{f.title}</h3>
                  <p className="text-sm text-muted-foreground">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
