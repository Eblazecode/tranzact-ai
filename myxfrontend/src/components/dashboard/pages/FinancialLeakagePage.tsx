import { useDashboardData } from "@/lib/DashboardContext";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from "recharts";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
const fmtShort = (v: number) => `\u20A6${(v / 1000).toFixed(0)}k`;
const COLORS = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)"];

export function FinancialLeakagePage() {
  // TODO: replace with API call - GET /dashboard/{id}/leakage
  const { leakage } = useDashboardData();

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Financial Leakage</p>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground">Total Leakage Amount</p>
          <p className="text-xl font-bold text-card-foreground mt-1">{fmt(leakage.totalLeakageAmount)}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground">Leakage %</p>
          <p className="text-xl font-bold text-card-foreground mt-1">{leakage.leakagePct.toFixed(2)}%</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground">Leakage Transaction Count</p>
          <p className="text-xl font-bold text-card-foreground mt-1">{leakage.leakageTransactionCount}</p>
        </div>
      </div>

      {/* Breakdown table */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6 overflow-x-auto">
        <p className="text-[13px] text-muted-foreground mb-4">Leakage Breakdown by Category</p>
        <table className="w-full text-sm min-w-[500px]">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 text-muted-foreground font-medium text-xs">Category</th>
              <th className="text-right py-2 text-muted-foreground font-medium text-xs">Total Amount</th>
              <th className="text-right py-2 text-muted-foreground font-medium text-xs">Count</th>
              <th className="text-right py-2 text-muted-foreground font-medium text-xs">Avg per transaction</th>
            </tr>
          </thead>
          <tbody>
            {leakage.breakdown.map((r) => (
              <tr key={r.category} className="border-b border-border/50">
                <td className="py-2.5 text-card-foreground">{r.category}</td>
                <td className="py-2.5 text-right text-card-foreground">{fmt(r.amount)}</td>
                <td className="py-2.5 text-right text-muted-foreground">{r.count}</td>
                <td className="py-2.5 text-right text-muted-foreground">{fmt(r.avg)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Donut */}
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground mb-4">Productive vs Leakage vs P2P vs POS vs Other</p>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={leakage.bucketBreakdown} dataKey="amount" nameKey="bucket" cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3}>
                {leakage.bucketBreakdown.map((_, i) => (<Cell key={i} fill={COLORS[i % COLORS.length]} />))}
              </Pie>
              <Tooltip content={({ active, payload }: any) => active && payload?.[0] ? (
                <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                  <p className="text-card-foreground">{payload[0].name}</p>
                  <p className="font-semibold text-card-foreground">{fmt(payload[0].value)}</p>
                </div>
              ) : null} />
              <Legend wrapperStyle={{ fontSize: 11, color: "var(--muted-foreground)" }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Bar */}
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground mb-4">Leakage Amount by Category</p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={leakage.amountByCategory}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="category" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
              <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
              <Tooltip content={({ active, payload, label }: any) => active && payload?.[0] ? (
                <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                  <p className="font-medium text-card-foreground">{label}</p>
                  <p className="font-semibold text-card-foreground">{fmt(payload[0].value)}</p>
                </div>
              ) : null} />
              <Bar dataKey="amount" fill="var(--primary)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
