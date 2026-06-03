import { useState, useEffect } from "react";
import { useDashboardData } from "@/lib/DashboardContext";
import { api } from "@/lib/api";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Legend, CartesianGrid } from "recharts";

const COLORS = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)", "var(--primary)"];
const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
const fmtShort = (v: number) => `\u20A6${(v / 1000).toFixed(0)}k`;

export function FilteredPieChartPage() {
  const { filteredPie: initialData, userName } = useDashboardData();
  const [month, setMonth] = useState(initialData.availableMonths[0] || "all");
  const [week, setWeek] = useState(initialData.availableWeeks[0] || "all");
  const [filterBy, setFilterBy] = useState<"month" | "week">("month");
  const [filteredPie, setFilteredPie] = useState(initialData);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const periodValue = filterBy === "month" ? month : week;
        const data = await api.getFilteredPieChart(userName, filterBy, periodValue);
        setFilteredPie(data);
      } catch (error) {
        console.error("Failed to fetch filtered pie chart data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [userName, filterBy, month, week]);

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Filtered Pie Chart</p>

      {/* Filter controls */}
      <div className="bg-card border border-border rounded-xl p-4 mb-6 flex flex-wrap gap-4">
        <div>
          <label className="text-xs text-muted-foreground mr-2">Filter By</label>
          <select value={filterBy} onChange={(e) => setFilterBy(e.target.value as "month" | "week")} className="bg-background border border-border rounded-md px-3 py-1.5 text-sm text-foreground">
            <option value="month">Month</option>
            <option value="week">Week</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-muted-foreground mr-2">Month</label>
          <select value={month} onChange={(e) => setMonth(e.target.value)} disabled={filterBy !== "month"} className="bg-background border border-border rounded-md px-3 py-1.5 text-sm text-foreground disabled:opacity-50">
            <option value="all">All</option>
            {filteredPie.availableMonths.map((m) => <option key={m}>{m}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-muted-foreground mr-2">Week</label>
          <select value={week} onChange={(e) => setWeek(e.target.value)} disabled={filterBy !== "week"} className="bg-background border border-border rounded-md px-3 py-1.5 text-sm text-foreground disabled:opacity-50">
            <option value="all">All</option>
            {filteredPie.availableWeeks.map((w) => <option key={w}>{w}</option>)}
          </select>
        </div>
        {loading && <span className="text-xs text-muted-foreground">Loading...</span>}
      </div>

      {/* Pie + Comparison Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground mb-4">Category Breakdown</p>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={filteredPie.categoryBreakdown} dataKey="amount" nameKey="category" cx="50%" cy="50%" outerRadius={100} paddingAngle={3}>
                {filteredPie.categoryBreakdown.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
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

        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground mb-4">
            Comparison Breakdown {filteredPie.comparisonPeriodLabel ? `(${filteredPie.comparisonPeriodLabel})` : ""}
          </p>
          {filteredPie.comparisonBreakdown.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={filteredPie.comparisonBreakdown}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="category" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} />
                <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
                <Tooltip content={({ active, payload, label }: any) => active && payload ? (
                  <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                    <p className="font-medium text-card-foreground mb-1">{label}</p>
                    {payload.map((p: any, i: number) => (
                      <p key={i} className="text-card-foreground">{p.name}: <span className="font-semibold">{fmt(p.value)}</span></p>
                    ))}
                  </div>
                ) : null} />
                <Legend wrapperStyle={{ fontSize: 11, color: "var(--muted-foreground)" }} />
                <Bar dataKey="current" name="Current" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="previous" name="Previous" fill="var(--chart-3)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-muted-foreground">Not enough data for comparison (need at least 2 periods).</p>
          )}
        </div>
      </div>

      {/* Monthly Pie Grid */}
      <div className="bg-card border border-border rounded-xl p-5">
        <p className="text-[13px] text-muted-foreground mb-4">Monthly Pie Grid</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {filteredPie.monthlyPieGrid.map((m) => (
            <div key={m.month} className="text-center">
              <ResponsiveContainer width="100%" height={120}>
                <PieChart>
                  <Pie data={m.slices} dataKey="amount" nameKey="category" cx="50%" cy="50%" outerRadius={45} paddingAngle={2}>
                    {m.slices.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip content={({ active, payload }: any) => active && payload?.[0] ? (
                    <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                      <p className="text-card-foreground">{payload[0].name}</p>
                      <p className="font-semibold text-card-foreground">{fmt(payload[0].value)}</p>
                    </div>
                  ) : null} />
                </PieChart>
              </ResponsiveContainer>
              <p className="text-xs text-muted-foreground mt-1">{m.month}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
