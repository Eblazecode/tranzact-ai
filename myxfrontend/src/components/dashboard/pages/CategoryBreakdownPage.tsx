import { useState } from "react";
import { useDashboardData } from "@/lib/DashboardContext";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;

type SortKey = "category" | "transactionCount" | "totalSpent" | "avgPerTransaction" | "maxTransaction" | "pctOfTotal";

export function CategoryBreakdownPage() {
  // TODO: replace with API call - GET /dashboard/{id}/category-breakdown
  const { categoryBreakdown } = useDashboardData();
  const [sortKey, setSortKey] = useState<SortKey>("totalSpent");
  const [asc, setAsc] = useState(false);

  const sorted = [...categoryBreakdown.rows].sort((a, b) => {
    const av = a[sortKey];
    const bv = b[sortKey];
    if (typeof av === "number" && typeof bv === "number") return asc ? av - bv : bv - av;
    return asc ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
  });

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setAsc(!asc);
    else { setSortKey(key); setAsc(false); }
  };

  const TH = ({ k, children, align = "left" }: { k: SortKey; children: React.ReactNode; align?: "left" | "right" }) => (
    <th className={`text-${align} py-2 text-muted-foreground font-medium text-xs cursor-pointer hover:text-foreground transition-colors`} onClick={() => toggleSort(k)}>
      {children} {sortKey === k && (asc ? "▲" : "▼")}
    </th>
  );

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Detailed Category Breakdown</p>

      {/* Text block */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="bg-card border border-border rounded-xl p-4">
          <p className="text-[13px] text-muted-foreground">Avg Daily Spend</p>
          <p className="text-lg font-bold text-card-foreground mt-1">{fmt(categoryBreakdown.avgDailySpend)}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-4">
          <p className="text-[13px] text-muted-foreground">Avg Monthly Spend</p>
          <p className="text-lg font-bold text-card-foreground mt-1">{fmt(categoryBreakdown.avgMonthlySpend)}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-4">
          <p className="text-[13px] text-muted-foreground">Most Active Category</p>
          <p className="text-lg font-bold text-card-foreground mt-1">{categoryBreakdown.mostActiveCategory}</p>
        </div>
      </div>

      {/* Table */}
      <div className="bg-card border border-border rounded-xl p-5 overflow-x-auto">
        <p className="text-[13px] text-muted-foreground mb-4">Category Breakdown</p>
        <table className="w-full text-sm min-w-[700px]">
          <thead>
            <tr className="border-b border-border">
              <TH k="category">Category</TH>
              <TH k="transactionCount" align="right">Transaction Count</TH>
              <TH k="totalSpent" align="right">Total Spent</TH>
              <TH k="avgPerTransaction" align="right">Avg Per Transaction</TH>
              <TH k="maxTransaction" align="right">Max Transaction</TH>
              <TH k="pctOfTotal" align="right">% of Total Spend</TH>
            </tr>
          </thead>
          <tbody>
            {sorted.map((r) => (
              <tr key={r.category} className="border-b border-border/50">
                <td className="py-2.5 text-card-foreground">{r.category}</td>
                <td className="py-2.5 text-right text-muted-foreground">{r.transactionCount}</td>
                <td className="py-2.5 text-right text-card-foreground">{fmt(r.totalSpent)}</td>
                <td className="py-2.5 text-right text-muted-foreground">{fmt(r.avgPerTransaction)}</td>
                <td className="py-2.5 text-right text-muted-foreground">{fmt(r.maxTransaction)}</td>
                <td className="py-2.5 text-right text-card-foreground">{r.pctOfTotal.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
