import type { DashboardOverviewCard } from "@/lib/api";
import { TrendingUp, TrendingDown } from "lucide-react";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;

function Card({
  label,
  value,
  change,
  positive,
}: {
  label: string;
  value: string;
  change: string;
  positive: boolean;
}) {
  return (
    <div className="bg-card border border-border rounded-xl p-5 transition-all duration-200 hover:shadow-md">
      <p className="text-[13px] text-muted-foreground">{label}</p>
      <p className="text-2xl font-bold text-card-foreground mt-2">{value}</p>
      <div className={`inline-flex items-center gap-1 mt-2 px-2 py-0.5 rounded-full text-xs font-medium ${positive ? "bg-green-500/10 text-green-600" : "bg-destructive/10 text-destructive"}`}>
        {positive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
        {change}
      </div>
    </div>
  );
}

export function StatCards({ cards }: { cards: DashboardOverviewCard[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card) => {
        const positive = card.changePct >= 0;
        const sign = positive ? "+" : "";
        return (
          <Card
            key={card.label}
            label={card.label}
            value={fmt(card.amount)}
            change={`${sign}${card.changePct.toFixed(1)}%`}
            positive={positive}
          />
        );
      })}
    </div>
  );
}
