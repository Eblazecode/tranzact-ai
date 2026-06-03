import { useState } from "react";
import { Lightbulb } from "lucide-react";
import { useDashboardData } from "@/lib/DashboardContext";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;

const RISK_COLORS: Record<string, string> = {
  HEALTHY: "text-green-500",
  MODERATE: "text-amber-500",
  "AT RISK": "text-destructive",
  CRITICAL: "text-destructive",
};

function HeaderCard({ label, value, valueClass = "text-card-foreground" }: { label: string; value: string; valueClass?: string }) {
  return (
    <div className="bg-card border border-border rounded-xl p-4">
      <p className="text-[13px] text-muted-foreground">{label}</p>
      <p className={`text-base font-bold mt-1 ${valueClass}`}>{value}</p>
    </div>
  );
}

export function RecommendationsPage() {
  // TODO: replace with API call - GET /dashboard/{id}/ai-recommendations
  const { aiRecommendations: r } = useDashboardData();
  const [dismissed, setDismissed] = useState<string[]>([]);
  const visible = r.cards.filter((c) => !dismissed.includes(c.id));
  const riskColor = RISK_COLORS[r.riskStatus] || "text-muted-foreground";

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">AI Recommendations</p>

      {/* Top Summary Header — 9 summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-6">
        <HeaderCard label="User Name" value={r.user} />
        <HeaderCard label="Health Score" value={`${r.healthScore}/${r.healthScoreMax}`} />
        <HeaderCard label="Risk Status" value={r.riskStatus} valueClass={riskColor} />
        <HeaderCard label="Total Income" value={fmt(r.totalIncome)} />
        <HeaderCard label="Total Spending" value={fmt(r.totalSpending)} />
        <HeaderCard label="Savings Rate" value={`${r.savingsRatePct.toFixed(1)}%`} valueClass={r.savingsRatePct < 0 ? "text-destructive" : "text-green-500"} />
        <HeaderCard label="Leakage" value={`${fmt(r.leakageAmount)} (${r.leakagePct}%)`} />
        <HeaderCard label="Top Category" value={`${r.topCategoryName} — ${fmt(r.topCategoryAmount)} (${r.topCategoryPct}%)`} />
        <HeaderCard label="Anomaly Status" value={r.anomalyStatus} />
      </div>

      <h2 className="text-lg font-bold text-foreground mb-4">AI Recommendations</h2>

      {/* Recommendation cards */}
      <div className="space-y-4 mb-6">
        {visible.map((c) => (
          <div key={c.id} className="bg-card border border-border rounded-xl p-5 transition-all duration-300 hover:border-primary/40">
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary/15 flex items-center justify-center">
                <Lightbulb className="h-5 w-5 text-primary" />
              </div>
              <div className="flex-1">
                <p className="text-[13px] text-muted-foreground mb-1">Recommendation #{c.number}</p>
                <p className="text-sm text-card-foreground leading-relaxed">{c.text}</p>
                <button
                  onClick={() => setDismissed((d) => [...d, c.id])}
                  className="mt-3 px-3 py-1 rounded-md text-xs font-medium bg-muted text-muted-foreground hover:bg-muted/80 transition-all duration-150"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Disclaimer */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-5">
        <p className="text-sm text-card-foreground leading-relaxed">
          <span className="font-semibold">Note:</span> These recommendations are generated from automated transaction analysis.
        </p>
      </div>
    </div>
  );
}
