import type { DashboardOverviewCategoryPoint } from "@/lib/api";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
const COLORS = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)", "var(--primary)"];

export function SpendingPieChart({ data }: { data: DashboardOverviewCategoryPoint[] }) {
  const total = data.reduce((s, c) => s + c.amount, 0);

  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <p className="text-[13px] text-muted-foreground mb-4">Spending by Category</p>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie data={data} dataKey="amount" nameKey="category" cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            content={({ active, payload }: any) =>
              active && payload?.[0] ? (
                <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                  <p className="text-card-foreground">{payload[0].name}</p>
                  <p className="font-semibold text-card-foreground">{fmt(payload[0].value)}</p>
                  <p className="text-xs text-muted-foreground">{total > 0 ? ((payload[0].value / total) * 100).toFixed(1) : "0.0"}%</p>
                </div>
              ) : null
            }
          />
          <Legend wrapperStyle={{ fontSize: 11, color: "var(--muted-foreground)" }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
