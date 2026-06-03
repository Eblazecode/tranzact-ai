import type { DashboardOverviewResponse } from "@/lib/api";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;

export function SpendingHighlights({
  highlights,
}: {
  highlights: DashboardOverviewResponse["spendingHighlights"];
}) {
  const highest = highlights.highestSingleSpend;
  const lowest = highlights.lowestSingleSpend;

  return (
    <div className="bg-card border border-border rounded-xl p-5 h-[420px]">
      <p className="text-[13px] text-muted-foreground mb-4">Spending Highlights</p>
      <div className="space-y-4">
        <div className="border-l-[3px] border-l-destructive pl-4 py-2">
          <p className="text-xs text-muted-foreground mb-1">Highest Single Spend</p>
          <p className="text-2xl font-bold text-destructive">{fmt(highest.amount)}</p>
          <p className="text-sm font-semibold text-card-foreground mt-2">{highest.description}</p>
          <p className="text-xs text-muted-foreground">{highest.date}</p>
        </div>
        <div className="border-l-[3px] border-l-green-500 pl-4 py-2">
          <p className="text-xs text-muted-foreground mb-1">Lowest Single Spend</p>
          <p className="text-2xl font-bold text-green-500">{fmt(lowest.amount)}</p>
          <p className="text-sm font-semibold text-card-foreground mt-2">{lowest.description}</p>
          <p className="text-xs text-muted-foreground">{lowest.date}</p>
        </div>
      </div>
    </div>
  );
}
