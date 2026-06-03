import { useDashboardData } from "@/lib/DashboardContext";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine, Cell, ComposedChart, Area } from "recharts";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
const fmtShort = (v: number) => `\u20A6${(v / 1000000).toFixed(2)}M`;

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-card border border-border rounded-xl p-4">
      <p className="text-[13px] text-muted-foreground">{label}</p>
      <p className="text-lg font-bold text-card-foreground mt-1">{value}</p>
      {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
    </div>
  );
}

export function BalanceTrajectoryPage() {
  // TODO: replace with API call - GET /dashboard/{id}/balance-trajectory
  const { balance } = useDashboardData();

  // Combine daily + rolling for overlay
  const merged = balance.dailyClosing.map((d, i) => ({
    date: d.date,
    balance: d.balance,
    rolling: balance.rolling30Day[i]?.balance ?? null,
  }));

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Balance Trajectory</p>

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        <StatCard label="Starting Balance" value={fmt(balance.startingBalance)} />
        <StatCard label="Ending Balance" value={fmt(balance.endingBalance)} />
        <StatCard label="Peak Balance" value={fmt(balance.peakBalance.amount)} sub={balance.peakBalance.date} />
        <StatCard label="Lowest Balance" value={fmt(balance.lowestBalance.amount)} sub={balance.lowestBalance.date} />
        <StatCard label="Avg Balance" value={fmt(balance.avgBalance)} />
        <StatCard label="Danger Zone Days" value={balance.dangerZoneDays.toString()} sub="Days below safe threshold" />
      </div>

      {/* Daily Closing + 30-Day Rolling */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-4">Daily Closing Balance & 30-Day Rolling Average</p>
        <ResponsiveContainer width="100%" height={350}>
          <ComposedChart data={merged}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} />
            <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <Tooltip content={({ active, payload, label }: any) => active && payload ? (
              <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                <p className="font-medium text-card-foreground">{label}</p>
                {payload.map((p: any, i: number) => (
                  <p key={i} className="text-card-foreground">{p.name}: <span className="font-semibold">{fmt(p.value)}</span></p>
                ))}
              </div>
            ) : null} />
            <Line dataKey="balance" name="Daily Balance" stroke="var(--chart-1)" strokeWidth={2} dot={false} />
            <Line dataKey="rolling" name="30-Day Rolling Avg" stroke="var(--primary)" strokeWidth={2} strokeDasharray="5 5" dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Monthly Average with Reference Line */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-4">Monthly Average Balance</p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={balance.monthlyAverage}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="month" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <Tooltip content={({ active, payload, label }: any) => active && payload?.[0] ? (
              <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                <p className="font-medium text-card-foreground">{label}</p>
                <p className="font-semibold text-card-foreground">{fmt(payload[0].value)}</p>
              </div>
            ) : null} />
            <ReferenceLine y={balance.avgBalance} stroke="var(--primary)" strokeDasharray="5 5" label={{ value: `Overall Avg ${fmtShort(balance.avgBalance)}`, position: "insideTopRight", fill: "var(--primary)", fontSize: 10 }} />
            <Bar dataKey="avgBalance" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Month-over-Month Change */}
      <div className="bg-card border border-border rounded-xl p-5">
        <p className="text-[13px] text-muted-foreground mb-4">Month-over-Month Change</p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={balance.monthOverMonthChange}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="month" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <YAxis tickFormatter={(v) => `\u20A6${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <Tooltip content={({ active, payload, label }: any) => active && payload?.[0] ? (
              <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                <p className="font-medium text-card-foreground">{label}</p>
                <p className="font-semibold text-card-foreground">{fmt(payload[0].value)}</p>
              </div>
            ) : null} />
            <ReferenceLine y={0} stroke="var(--border)" />
            <Bar dataKey="change" radius={[4, 4, 0, 0]}>
              {balance.monthOverMonthChange.map((d, i) => (
                <Cell key={i} fill={d.change < 0 ? "var(--destructive)" : "var(--chart-1)"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
