import { useDashboardData } from "@/lib/DashboardContext";
import { BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
const fmtShort = (v: number) => `\u20A6${(v / 1000).toFixed(0)}k`;

export function AnomalyDetectionPage() {
  // TODO: replace with API call - GET /dashboard/{id}/anomalies
  const { anomaly } = useDashboardData();

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Anomaly Detection</p>

      {/* Text block */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground mb-3">Flagged Anomaly Months</p>
          {anomaly.flaggedMonths.length === 0 ? (
            <p className="text-sm text-muted-foreground">None detected</p>
          ) : (
            <ul className="space-y-2">
              {anomaly.flaggedMonths.map((m) => (
                <li key={m.month} className="text-sm text-card-foreground flex justify-between border-b border-border/50 pb-2 last:border-0">
                  <span>{m.month}</span>
                  <span className="text-muted-foreground">{fmt(m.amount)} · z={m.zScore.toFixed(2)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground mb-3">Flagged Anomaly Weeks</p>
          {anomaly.flaggedWeeks.length === 0 ? (
            <p className="text-sm text-muted-foreground">None detected</p>
          ) : (
            <ul className="space-y-2">
              {anomaly.flaggedWeeks.map((w) => (
                <li key={w.week} className="text-sm text-card-foreground flex justify-between border-b border-border/50 pb-2 last:border-0">
                  <span>{w.week}</span>
                  <span className="text-muted-foreground">{fmt(w.amount)} · z={w.zScore.toFixed(2)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Monthly chart */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-4">Monthly Anomaly Chart</p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={anomaly.monthlySeries}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="month" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <Tooltip content={({ active, payload, label }: any) => active && payload?.[0] ? (
              <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                <p className="font-medium text-card-foreground">{label}</p>
                <p className="font-semibold text-card-foreground">{fmt(payload[0].value)}</p>
                {payload[0].payload.isAnomaly && <p className="text-destructive text-xs mt-1">Flagged anomaly</p>}
              </div>
            ) : null} />
            <Bar dataKey="amount" radius={[4, 4, 0, 0]}>
              {anomaly.monthlySeries.map((d, i) => (
                <Cell key={i} fill={d.isAnomaly ? "var(--destructive)" : "var(--chart-1)"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Weekly chart */}
      <div className="bg-card border border-border rounded-xl p-5">
        <p className="text-[13px] text-muted-foreground mb-4">Weekly Anomaly Chart</p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={anomaly.weeklySeries}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="week" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <Tooltip content={({ active, payload, label }: any) => active && payload?.[0] ? (
              <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                <p className="font-medium text-card-foreground">{label}</p>
                <p className="font-semibold text-card-foreground">{fmt(payload[0].value)}</p>
                {payload[0].payload.isAnomaly && <p className="text-destructive text-xs mt-1">Flagged anomaly</p>}
              </div>
            ) : null} />
            <Bar dataKey="amount" radius={[4, 4, 0, 0]}>
              {anomaly.weeklySeries.map((d, i) => (
                <Cell key={i} fill={d.isAnomaly ? "var(--destructive)" : "var(--chart-2)"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
