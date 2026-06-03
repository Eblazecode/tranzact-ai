import { useDashboardData } from "@/lib/DashboardContext";
import { BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
const fmtShort = (v: number) => `\u20A6${(v / 1000).toFixed(0)}k`;

// Light-blue → dark-blue gradient based on intensity
function blueShade(intensity: number) {
  const lightness = 0.85 - intensity * 0.45;
  return `oklch(${lightness} 0.15 240)`;
}
// Light-peach → dark-red gradient
function peachToRedShade(intensity: number) {
  const lightness = 0.85 - intensity * 0.4;
  const chroma = 0.1 + intensity * 0.18;
  const hue = 30 - intensity * 10;
  return `oklch(${lightness} ${chroma} ${hue})`;
}

export function RecurringTransactionsPage() {
  // TODO: replace with API call - GET /dashboard/{id}/recurring
  const { recurring } = useDashboardData();

  const monthsActiveData = recurring.rows.map((r) => ({ description: r.description, value: r.monthsRepeated, total: r.totalMonths }));
  const avgAmountData = recurring.rows.map((r) => ({ description: r.description, value: r.avgAmount }));
  const maxMonths = Math.max(...monthsActiveData.map((d) => d.value));
  const maxAvg = Math.max(...avgAmountData.map((d) => d.value));

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Recurring Transactions</p>

      {/* Table */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6 overflow-x-auto">
        <p className="text-[13px] text-muted-foreground mb-4">Recurring Items</p>
        <table className="w-full text-sm min-w-[500px]">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 text-muted-foreground font-medium text-xs">Description</th>
              <th className="text-right py-2 text-muted-foreground font-medium text-xs">Frequency %</th>
              <th className="text-right py-2 text-muted-foreground font-medium text-xs">Months Repeated</th>
            </tr>
          </thead>
          <tbody>
            {recurring.rows.map((r) => (
              <tr key={r.description} className="border-b border-border/50">
                <td className="py-2.5 text-card-foreground">{r.description}</td>
                <td className="py-2.5 text-right text-card-foreground">{r.frequencyPct}%</td>
                <td className="py-2.5 text-right text-muted-foreground">{r.monthsRepeated} / {r.totalMonths}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pattern summary */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-2">Recurring Pattern Summary</p>
        <p className="text-sm text-card-foreground leading-relaxed">{recurring.patternSummary}</p>
      </div>

      {/* Months Active chart */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-4">Months Active (out of total)</p>
        <ResponsiveContainer width="100%" height={monthsActiveData.length * 36 + 30}>
          <BarChart data={monthsActiveData} layout="vertical" margin={{ left: 10, right: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis type="number" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <YAxis dataKey="description" type="category" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} width={170} />
            <Tooltip content={({ active, payload }: any) => active && payload?.[0] ? (
              <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                <p className="text-card-foreground">{payload[0].payload.description}</p>
                <p className="font-semibold text-card-foreground">{payload[0].value} / {payload[0].payload.total} months</p>
              </div>
            ) : null} />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {monthsActiveData.map((d, i) => <Cell key={i} fill={blueShade(d.value / maxMonths)} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Average Amount per Occurrence */}
      <div className="bg-card border border-border rounded-xl p-5">
        <p className="text-[13px] text-muted-foreground mb-4">Average Amount per Occurrence</p>
        <ResponsiveContainer width="100%" height={avgAmountData.length * 36 + 30}>
          <BarChart data={avgAmountData} layout="vertical" margin={{ left: 10, right: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis type="number" tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <YAxis dataKey="description" type="category" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} width={170} />
            <Tooltip content={({ active, payload }: any) => active && payload?.[0] ? (
              <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                <p className="text-card-foreground">{payload[0].payload.description}</p>
                <p className="font-semibold text-card-foreground">{fmt(payload[0].value)}</p>
              </div>
            ) : null} />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {avgAmountData.map((d, i) => <Cell key={i} fill={peachToRedShade(d.value / maxAvg)} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
