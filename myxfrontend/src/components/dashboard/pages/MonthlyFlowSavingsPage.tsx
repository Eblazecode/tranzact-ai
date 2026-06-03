import { useDashboardData } from "@/lib/DashboardContext";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell, ReferenceLine } from "recharts";

const fmtShort = (v: number) => `\u20A6${(v / 1000).toFixed(0)}k`;
const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;

function NetTip({ active, payload, label }: any) {
  if (!active || !payload?.[0]) return null;
  return (
    <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
      <p className="font-medium text-card-foreground">{label}</p>
      <p className="text-card-foreground">Net Savings: <span className="font-semibold">{fmt(payload[0].value)}</span></p>
    </div>
  );
}

function RateTip({ active, payload, label }: any) {
  if (!active || !payload?.[0]) return null;
  return (
    <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
      <p className="font-medium text-card-foreground">{label}</p>
      <p className="text-card-foreground">Savings Rate: <span className="font-semibold">{payload[0].value}%</span></p>
    </div>
  );
}

export function MonthlyFlowSavingsPage() {
  // TODO: replace with API call - GET /dashboard/{id}/monthly-flow
  const { monthlyFlow } = useDashboardData();

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Monthly Financial Flow & Savings Rate</p>

      {/* Net Savings */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-4">Monthly Net Savings</p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={monthlyFlow.monthlyNetSavings}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="month" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <Tooltip content={<NetTip />} />
            <ReferenceLine y={0} stroke="var(--border)" />
            <Bar dataKey="netSavings" radius={[4, 4, 0, 0]}>
              {monthlyFlow.monthlyNetSavings.map((d, i) => (
                <Cell key={i} fill={d.netSavings < 0 ? "var(--destructive)" : "var(--chart-1)"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Savings Rate Line */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-4">Monthly Savings Rate %</p>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={monthlyFlow.monthlySavingsRate}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="month" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <Tooltip content={<RateTip />} />
            <ReferenceLine y={20} stroke="var(--primary)" strokeDasharray="5 5" label={{ value: "Healthy ≥ 20%", position: "insideTopRight", fill: "var(--primary)", fontSize: 10 }} />
            <ReferenceLine y={0} stroke="var(--border)" />
            <Line dataKey="ratePct" stroke="var(--primary)" strokeWidth={2} dot={{ fill: "var(--primary)", r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Text block */}
      <div className="bg-card border border-border rounded-xl p-5">
        <p className="text-[13px] text-muted-foreground mb-2">Threshold Explanation</p>
        <p className="text-sm text-card-foreground leading-relaxed mb-3">{monthlyFlow.thresholdExplanation}</p>
        <p className="text-sm font-semibold text-primary">{monthlyFlow.healthyThresholdNote}</p>
      </div>
    </div>
  );
}
