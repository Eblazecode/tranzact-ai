import { useState, useEffect } from "react";
import { useDashboardData } from "@/lib/DashboardContext";
import { api } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
const fmtShort = (v: number) => `\u20A6${(v / 1000).toFixed(0)}k`;

export function RecipientsPage() {
  const { recipients: initialData, userName } = useDashboardData();
  const [month, setMonth] = useState(initialData.availableMonths[0] || "all");
  const [week, setWeek] = useState(initialData.availableWeeks[0] || "all");
  const [year, setYear] = useState(initialData.availableYears[0] || "all");
  const [filterBy, setFilterBy] = useState<"month" | "week" | "year">("month");
  const [recipients, setRecipients] = useState(initialData);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const periodValue = filterBy === "month" ? month : filterBy === "week" ? week : year;
        const data = await api.getTransfersOut(userName, filterBy, periodValue, 10);
        setRecipients(data);
      } catch (error) {
        console.error("Failed to fetch recipients data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [userName, filterBy, month, week, year]);

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Who You Send Money To</p>

      {/* Filters */}
      <div className="bg-card border border-border rounded-xl p-4 mb-6 flex flex-wrap gap-4">
        <div>
          <label className="text-xs text-muted-foreground mr-2">Filter By</label>
          <select value={filterBy} onChange={(e) => setFilterBy(e.target.value as "month" | "week" | "year")} className="bg-background border border-border rounded-md px-3 py-1.5 text-sm text-foreground">
            <option value="month">Month</option>
            <option value="week">Week</option>
            <option value="year">Year</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-muted-foreground mr-2">Month</label>
          <select value={month} onChange={(e) => setMonth(e.target.value)} disabled={filterBy !== "month"} className="bg-background border border-border rounded-md px-3 py-1.5 text-sm text-foreground disabled:opacity-50">
            <option value="all">All</option>
            {recipients.availableMonths.map((m) => <option key={m}>{m}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-muted-foreground mr-2">Week</label>
          <select value={week} onChange={(e) => setWeek(e.target.value)} disabled={filterBy !== "week"} className="bg-background border border-border rounded-md px-3 py-1.5 text-sm text-foreground disabled:opacity-50">
            <option value="all">All</option>
            {recipients.availableWeeks.map((w) => <option key={w}>{w}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-muted-foreground mr-2">Year</label>
          <select value={year} onChange={(e) => setYear(e.target.value)} disabled={filterBy !== "year"} className="bg-background border border-border rounded-md px-3 py-1.5 text-sm text-foreground disabled:opacity-50">
            <option value="all">All</option>
            {recipients.availableYears.map((y) => <option key={y}>{y}</option>)}
          </select>
        </div>
        {loading && <span className="text-xs text-muted-foreground">Loading...</span>}
      </div>

      {/* Table */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6 overflow-x-auto">
        <p className="text-[13px] text-muted-foreground mb-4">Recipients</p>
        <table className="w-full text-sm min-w-[400px]">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 text-muted-foreground font-medium text-xs">Recipient Name</th>
              <th className="text-right py-2 text-muted-foreground font-medium text-xs">Frequency Sent</th>
              <th className="text-right py-2 text-muted-foreground font-medium text-xs">Total Amount Sent</th>
            </tr>
          </thead>
          <tbody>
            {recipients.table.map((r) => (
              <tr key={r.name} className="border-b border-border/50">
                <td className="py-2.5 text-card-foreground">{r.name}</td>
                <td className="py-2.5 text-right text-muted-foreground">{r.frequency}</td>
                <td className="py-2.5 text-right text-card-foreground">{fmt(r.totalSent)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Two charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground mb-4">Transfer Count by Recipient</p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={recipients.transferCountByRecipient}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} />
              <YAxis tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
              <Tooltip content={({ active, payload, label }: any) => active && payload?.[0] ? (
                <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                  <p className="font-medium text-card-foreground">{label}</p>
                  <p className="font-semibold text-card-foreground">{payload[0].value} transfers</p>
                </div>
              ) : null} />
              <Bar dataKey="count" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-[13px] text-muted-foreground mb-4">Amount Sent by Recipient</p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={recipients.amountSentByRecipient}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} />
              <YAxis tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
              <Tooltip content={({ active, payload, label }: any) => active && payload?.[0] ? (
                <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                  <p className="font-medium text-card-foreground">{label}</p>
                  <p className="font-semibold text-card-foreground">{fmt(payload[0].value)}</p>
                </div>
              ) : null} />
              <Bar dataKey="amount" fill="var(--chart-2)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
