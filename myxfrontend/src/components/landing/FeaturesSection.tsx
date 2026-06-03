import {
  BarChart3,
  Brain,
  Shield,
  Zap,
  PieChart,
  TrendingUp,
  AlertTriangle,
  Users,
} from "lucide-react";

const features = [
  {
    icon: Zap,
    title: "Instant Processing",
    bullets: [
      "Upload any supported bank statement format",
      "Auto-cleaned and structured in under 60 seconds",
    ],
  },
  {
    icon: BarChart3,
    title: "Spending Analysis",
    bullets: [
      "Category breakdowns, daily trends, day-of-week patterns",
      "Top 10 largest transactions highlighted",
    ],
  },
  {
    icon: PieChart,
    title: "Category Breakdown",
    bullets: [
      "Interactive donut charts filterable by month or week",
      "Progress bars showing % of total spend",
    ],
  },
  {
    icon: Brain,
    title: "AI Predictions",
    bullets: [
      "Gradient Boosting predicts next month's spending",
      "SHAP explanations in plain English",
    ],
  },
  {
    icon: TrendingUp,
    title: "Financial Health",
    bullets: [
      "Health score from 0–100 with colour-coded signals",
      "Savings rate, balance stability, overspend risk",
    ],
  },
  {
    icon: AlertTriangle,
    title: "Anomaly Detection",
    bullets: [
      "Flags unusual transactions with severity levels",
      "Dismissible alert cards with plain-language reasons",
    ],
  },
  {
    icon: Users,
    title: "Recipient Analysis",
    bullets: [
      "See who you send money to most — by frequency and amount",
      "Filter by week, month, or year",
    ],
  },
  {
    icon: Shield,
    title: "Bank-Grade Privacy",
    bullets: [
      "Your data never leaves our secure servers",
      "No bank connections — we only process files you upload",
    ],
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="py-24 bg-navy text-navy-foreground">
      <div className="mx-auto max-w-7xl px-4">
        <div className="text-center mb-16">
          <p className="text-sm font-semibold uppercase tracking-widest text-primary mb-3">
            ✦ Powered by AI
          </p>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
            Understanding your money shouldn't be hard.{" "}
            <span className="text-primary">TransacAI makes it easy.</span>
          </h2>
          <p className="text-navy-foreground/70 max-w-2xl mx-auto text-lg">
            Disconnected bank statements and scattered data slow you down. TransacAI connects
            everything in one place to make understanding your finances easier than you think.
          </p>
        </div>

        {/* HubSpot-style feature grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="group rounded-2xl border border-navy-foreground/10 bg-navy-foreground/5 p-6 hover:bg-navy-foreground/10 hover:border-primary/30 transition-all duration-300"
            >
              <div className="h-12 w-12 rounded-xl bg-primary/15 flex items-center justify-center mb-5">
                <f.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-3">{f.title}</h3>
              <hr className="border-navy-foreground/10 mb-3" />
              <ul className="space-y-2">
                {f.bullets.map((b, i) => (
                  <li key={i} className="text-sm text-navy-foreground/70 leading-relaxed flex gap-2">
                    <span className="text-primary mt-0.5">•</span>
                    {b}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
