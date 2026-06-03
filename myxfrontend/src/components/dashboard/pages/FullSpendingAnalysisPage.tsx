import { useDashboardData } from "@/lib/DashboardContext";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid, Cell,
  PieChart, Pie, AreaChart, Area, LineChart, Line,
} from "recharts";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
const fmtShort = (v: number) => `\u20A6${(v / 1000).toFixed(0)}k`;
const COLORS = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)", "var(--primary)"];

function Tip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
      {label && <p className="font-medium text-card-foreground mb-1">{label}</p>}
      {payload.map((p: any, i: number) => (
        <p key={i} className="text-card-foreground">
          {p.name}: <span className="font-semibold">{typeof p.value === "number" ? fmt(p.value) : p.value}</span>
        </p>
      ))}
    </div>
  );
}

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-card border border-border rounded-xl p-4">
      <p className="text-[13px] text-muted-foreground">{label}</p>
      <p className="text-lg font-bold text-card-foreground mt-1 truncate">{value}</p>
      {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
    </div>
  );
}

export function FullSpendingAnalysisPage() {
  // TODO: replace with API call - GET /dashboard/{id}/full-spending-analysis
  const { fsa } = useDashboardData();

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Full Spending Analysis</p>

      {/* Date range text block */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-2">Date Range</p>
        <p className="text-sm text-card-foreground leading-relaxed">{fsa.dateRangeText}</p>
      </div>

      {/* 10 summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        <StatCard label="Transaction Count" value={fsa.transactionCount.toLocaleString("en-NG")} />
        <StatCard label="Total Spent" value={fmt(fsa.totalSpent)} />
        <StatCard label="Total Received" value={fmt(fsa.totalReceived)} />
        <StatCard label="Net Position" value={fmt(fsa.netPosition)} />
        <StatCard label="Highest Spending Month" value={fsa.highestSpendingMonth.month} sub={fmt(fsa.highestSpendingMonth.amount)} />
        <StatCard label="Lowest Spending Month" value={fsa.lowestSpendingMonth.month} sub={fmt(fsa.lowestSpendingMonth.amount)} />
        <StatCard label="Highest Balance" value={fmt(fsa.highestBalance.amount)} sub={fsa.highestBalance.date} />
        <StatCard label="Lowest Balance" value={fmt(fsa.lowestBalance.amount)} sub={fsa.lowestBalance.date} />
        <StatCard label="Current Balance" value={fmt(fsa.currentBalance)} />
        <StatCard label="Highest Spending Category" value={fsa.highestSpendingCategory.name} sub={fmt(fsa.highestSpendingCategory.amount)} />
      </div>

      {/* Total Spend by Category — Horizontal Bar */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-4">Total Spend by Category</p>
        <ResponsiveContainer width="100%" height={fsa.spendByCategory.length * 38 + 30}>
          <BarChart data={[...fsa.spendByCategory].sort((a, b) => b.amount - a.amount)} layout="vertical" margin={{ left: 10, right: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis type="number" tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <YAxis dataKey="category" type="category" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} width={130} />
            <Tooltip content={<Tip />} />
            <Bar dataKey="amount" name="Spend" fill="var(--chart-1)" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Income vs Expenses — Grouped Vertical Bars */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-4">Monthly Income vs Expenses</p>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={fsa.monthlyIncomeVsExpenses}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="month" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <Tooltip content={<Tip />} />
            <Legend wrapperStyle={{ fontSize: 12, color: "var(--muted-foreground)" }} />
            <Bar dataKey="income" name="Income" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="expenses" name="Expenses" fill="var(--chart-3)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Pie — Transaction count by category */}
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground mb-4">Transaction Count by Category</p>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={fsa.transactionCountByCategory} dataKey="count" nameKey="category" cx="50%" cy="50%" outerRadius={100} paddingAngle={3}>
                {fsa.transactionCountByCategory.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }: any) =>
                  active && payload?.[0] ? (
                    <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                      <p className="text-card-foreground">{payload[0].name}</p>
                      <p className="font-semibold text-card-foreground">{payload[0].value} transactions</p>
                    </div>
                  ) : null
                }
              />
              <Legend wrapperStyle={{ fontSize: 11, color: "var(--muted-foreground)" }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Spending by Day of Week */}
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground mb-4">Spending by Day of Week</p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={fsa.spendingByDayOfWeek}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="day" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
              <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
              <Tooltip content={<Tip />} />
              <Bar dataKey="amount" name="Spend" fill="var(--chart-2)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Daily Spending Trend — Area + Line */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-4">Daily Spending Trend</p>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={fsa.dailySpendingTrend}>
            <defs>
              <linearGradient id="dailyGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} />
            <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <Tooltip content={<Tip />} />
            <Area type="monotone" dataKey="amount" name="Daily Spend" stroke="var(--primary)" strokeWidth={2} fill="url(#dailyGrad)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Top 10 Largest Transactions — Horizontal Bar */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <p className="text-[13px] text-muted-foreground mb-4">Top 10 Largest Transactions</p>
        <ResponsiveContainer width="100%" height={fsa.top10LargestTransactions.length * 36 + 30}>
          <BarChart data={fsa.top10LargestTransactions} layout="vertical" margin={{ left: 10, right: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis type="number" tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
            <YAxis dataKey="desc" type="category" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} width={200} />
            <Tooltip content={<Tip />} />
            <Bar dataKey="amount" name="Amount" fill="var(--chart-3)" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Summary notes text block */}
      <div className="bg-card border border-border rounded-xl p-5">
        <p className="text-[13px] text-muted-foreground mb-2">Financial Summary Notes</p>
        <p className="text-sm text-card-foreground leading-relaxed">{fsa.summaryNotes}</p>
      </div>
    </div>
  );
}
