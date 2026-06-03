import type { DashboardOverviewFlowPoint } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from "recharts";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
const fmtShort = (v: number) => `\u20A6${(v / 1000).toFixed(0)}k`;

export function MonthlyFlowChart({ data }: { data: DashboardOverviewFlowPoint[] }) {
  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <p className="text-[13px] text-muted-foreground mb-4">Monthly Financial Flow</p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="month" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
          <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
          <Tooltip
            content={({ active, payload, label }: any) =>
              active && payload?.length ? (
                <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                  <p className="font-medium text-card-foreground mb-1">{label}</p>
                  {payload.map((p: any, i: number) => (
                    <p key={i} className="text-card-foreground">
                      {p.name}: <span className="font-semibold">{fmt(p.value)}</span>
                    </p>
                  ))}
                </div>
              ) : null
            }
          />
          <Legend wrapperStyle={{ fontSize: 12, color: "var(--muted-foreground)" }} />
          <Bar dataKey="income" name="Credits" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
          <Bar dataKey="expenses" name="Debits" fill="var(--chart-3)" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
