import { useDashboardData } from "@/lib/DashboardContext";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;

const STATUS_COLORS: Record<string, string> = {
  Healthy: "text-green-500",
  Moderate: "text-amber-500",
  "At Risk": "text-destructive",
  Critical: "text-destructive",
};

export function FinancialHealthPage() {
  // TODO: replace with API call - GET /dashboard/{id}/health
  const { health } = useDashboardData();
  const statusColor = STATUS_COLORS[health.healthStatus] || "text-muted-foreground";

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Financial Health Summary</p>

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground">Total Income</p>
          <p className="text-xl font-bold text-card-foreground mt-1">{fmt(health.totalIncome)}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground">Total Expenses</p>
          <p className="text-xl font-bold text-card-foreground mt-1">{fmt(health.totalExpenses)}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground">Net Savings</p>
          <p className={`text-xl font-bold mt-1 ${health.netSavings < 0 ? "text-destructive" : "text-green-500"}`}>{fmt(health.netSavings)}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground">Savings Rate</p>
          <p className={`text-xl font-bold mt-1 ${health.savingsRatePct < 0 ? "text-destructive" : "text-green-500"}`}>{health.savingsRatePct.toFixed(1)}%</p>
        </div>
      </div>

      {/* Status text block */}
      <div className="bg-card border border-border rounded-xl p-6">
        <p className="text-[13px] text-muted-foreground mb-3">Health Status</p>
        <p className={`text-2xl font-bold mb-3 ${statusColor}`}>{health.healthStatus}</p>
        <p className="text-sm text-card-foreground leading-relaxed">{health.healthNarrative}</p>
        <p className="text-xs text-muted-foreground mt-4">Health Score: {health.healthScore}/85</p>
      </div>
    </div>
  );
}
