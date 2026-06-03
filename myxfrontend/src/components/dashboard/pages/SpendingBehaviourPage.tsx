import { useDashboardData } from "@/lib/DashboardContext";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;

export function SpendingBehaviourPage() {
  // TODO: replace with API call - GET /dashboard/{id}/behaviour
  const { behaviour } = useDashboardData();

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Spending Behaviour Patterns</p>

      {/* Text block — weekend vs weekday + month info */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-card border border-border rounded-xl p-4">
          <p className="text-[13px] text-muted-foreground">Weekend Total</p>
          <p className="text-lg font-bold text-card-foreground mt-1">{fmt(behaviour.weekendTotal)}</p>
          <p className="text-xs text-muted-foreground">Avg {fmt(behaviour.weekendAvg)}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-4">
          <p className="text-[13px] text-muted-foreground">Weekday Total</p>
          <p className="text-lg font-bold text-card-foreground mt-1">{fmt(behaviour.weekdayTotal)}</p>
          <p className="text-xs text-muted-foreground">Avg {fmt(behaviour.weekdayAvg)}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-4">
          <p className="text-[13px] text-muted-foreground">Most Expensive Month</p>
          <p className="text-lg font-bold text-card-foreground mt-1">{behaviour.mostExpensiveMonth.month}</p>
          <p className="text-xs text-muted-foreground">{fmt(behaviour.mostExpensiveMonth.amount)}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-4">
          <p className="text-[13px] text-muted-foreground">Cheapest Month</p>
          <p className="text-lg font-bold text-card-foreground mt-1">{behaviour.cheapestMonth.month}</p>
          <p className="text-xs text-muted-foreground">{fmt(behaviour.cheapestMonth.amount)}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-4">
          <p className="text-[13px] text-muted-foreground">Avg Monthly Spend</p>
          <p className="text-lg font-bold text-card-foreground mt-1">{fmt(behaviour.avgMonthlySpend)}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-4">
          <p className="text-[13px] text-muted-foreground">Std Deviation</p>
          <p className="text-lg font-bold text-card-foreground mt-1">{fmt(behaviour.stdDeviation)}</p>
        </div>
      </div>

      {/* Size distribution table */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6 overflow-x-auto">
        <p className="text-[13px] text-muted-foreground mb-4">Transaction Size Distribution</p>
        <table className="w-full text-sm min-w-[500px]">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 text-muted-foreground font-medium text-xs">Bucket</th>
              <th className="text-left py-2 text-muted-foreground font-medium text-xs">Range</th>
              <th className="text-right py-2 text-muted-foreground font-medium text-xs">Count</th>
              <th className="text-right py-2 text-muted-foreground font-medium text-xs">Total</th>
            </tr>
          </thead>
          <tbody>
            {behaviour.sizeDistribution.map((b) => (
              <tr key={b.bucket} className="border-b border-border/50">
                <td className="py-2.5 text-card-foreground font-medium">{b.bucket}</td>
                <td className="py-2.5 text-muted-foreground">{b.range}</td>
                <td className="py-2.5 text-right text-muted-foreground">{b.count}</td>
                <td className="py-2.5 text-right text-card-foreground">{fmt(b.total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Category Consistency progress bars */}
      <div className="bg-card border border-border rounded-xl p-5">
        <p className="text-[13px] text-muted-foreground mb-4">Category Consistency</p>
        <div className="space-y-3">
          {behaviour.categoryConsistency.map((c) => (
            <div key={c.category}>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-card-foreground">{c.category}</span>
                <span className="text-sm text-muted-foreground">{c.consistencyPct}%</span>
              </div>
              <div className="h-2.5 bg-muted rounded-full overflow-hidden">
                <div className="h-full rounded-full bg-primary transition-all duration-300" style={{ width: `${c.consistencyPct}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
