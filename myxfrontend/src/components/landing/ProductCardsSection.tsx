import { BarChart3, Brain, Lightbulb, TrendingUp } from "lucide-react";

const cards = [
  { icon: BarChart3, title: "Spending Insights", desc: "11 deep analytics from every transaction" },
  { icon: Brain, title: "AI Predictions", desc: "Know what you'll spend before the month starts" },
  { icon: TrendingUp, title: "Explainable AI", desc: "Understand exactly why the AI made each prediction" },
  { icon: Lightbulb, title: "Smart Recommendations", desc: "Personalised actions to improve your finances" },
];

export function ProductCardsSection() {
  return (
    <section className="py-24 bg-background">
      <div className="mx-auto max-w-7xl px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-4">
            Your complete financial intelligence stack
          </h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {cards.map((c) => (
            <div
              key={c.title}
              className="bg-card border border-border rounded-2xl p-8 transition-all duration-200 hover:-translate-y-1.5 hover:shadow-[0_12px_30px_-8px_var(--color-primary)/0.15]"
            >
              <div className="w-12 h-12 rounded-xl bg-primary/15 flex items-center justify-center mb-5">
                <c.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-bold text-card-foreground mb-2">{c.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{c.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
