import { startTransition, useEffect, useState } from "react";

import { api, type DashboardOverviewResponse } from "@/lib/api";
import { useDashboardData } from "@/lib/DashboardContext";
import { getCurrentUserName } from "@/lib/auth";

import { StatCards } from "./StatCards";
import { MonthlyFlowChart } from "./MonthlyFlowChart";
import { SpendingPieChart } from "./SpendingPieChart";
import { TransactionHistory } from "./TransactionHistory";
import { SpendingHighlights } from "./SpendingHighlights";

const EMPTY_OVERVIEW: DashboardOverviewResponse = {
  summaryCards: [
    { label: "Total Balance", amount: 0, changePct: 0 },
    { label: "Net Position", amount: 0, changePct: 0 },
    { label: "Total Credit", amount: 0, changePct: 0 },
    { label: "Total Debit", amount: 0, changePct: 0 },
  ],
  monthlyFinancialFlow: [],
  spendingByCategory: [],
  transactionHistory: [],
  spendingHighlights: {
    highestSingleSpend: { amount: 0, description: "-", date: "-" },
    lowestSingleSpend: { amount: 0, description: "-", date: "-" },
  },
};

function buildFallbackOverview(
  userData: ReturnType<typeof useDashboardData>,
): DashboardOverviewResponse {
  const lowestTransaction =
    userData.fsa.top10LargestTransactions[userData.fsa.top10LargestTransactions.length - 1];

  return {
    summaryCards: [
      { label: "Total Balance", amount: userData.fsa.currentBalance, changePct: 0 },
      { label: "Net Position", amount: userData.fsa.netPosition, changePct: 0 },
      { label: "Total Credit", amount: userData.fsa.totalReceived, changePct: 0 },
      { label: "Total Debit", amount: userData.fsa.totalSpent, changePct: 0 },
    ],
    monthlyFinancialFlow: userData.fsa.monthlyIncomeVsExpenses,
    spendingByCategory: userData.fsa.spendByCategory,
    transactionHistory: userData.fsa.top10LargestTransactions.map((item) => ({
      description: item.desc,
      category: (item as any).category ?? "Uncategorized",
      date: item.date,
      amount: item.amount,
    })),
    spendingHighlights: {
      highestSingleSpend: userData.fsa.top10LargestTransactions[0]
        ? {
            amount: userData.fsa.top10LargestTransactions[0].amount,
            description: userData.fsa.top10LargestTransactions[0].desc,
            date: userData.fsa.top10LargestTransactions[0].date,
          }
        : EMPTY_OVERVIEW.spendingHighlights.highestSingleSpend,
      lowestSingleSpend: lowestTransaction
        ? {
            amount: lowestTransaction.amount,
            description: lowestTransaction.desc,
            date: lowestTransaction.date,
          }
        : EMPTY_OVERVIEW.spendingHighlights.lowestSingleSpend,
    },
  };
}

export function DashboardOverview({ refreshKey = 0 }: { refreshKey?: number }) {
  const dashboardData = useDashboardData();
  const userName = dashboardData.userName || getCurrentUserName();
  const [overview, setOverview] = useState<DashboardOverviewResponse>(() => buildFallbackOverview(dashboardData));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    api.getDashboardOverview(userName)
      .then((payload) => {
        if (cancelled) return;
        startTransition(() => {
          setOverview(payload);
          setError(null);
          setLoading(false);
        });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        startTransition(() => {
          setOverview(buildFallbackOverview(dashboardData));
          setError(err instanceof Error ? err.message : "Failed to load dashboard overview.");
          setLoading(false);
        });
      });

    return () => {
      cancelled = true;
    };
  }, [dashboardData, refreshKey, userName]);

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Dashboard Overview</p>
      {loading ? (
        <div className="mb-4 rounded-xl border border-border bg-primary/5 px-4 py-3 text-sm text-foreground">
          Loading dashboard overview...
        </div>
      ) : null}
      {error ? (
        <div className="mb-4 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-foreground">
          Dashboard overview is using fallback data. {error}
        </div>
      ) : null}
      <StatCards cards={overview.summaryCards} />
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 mb-6">
        <div className="lg:col-span-3"><MonthlyFlowChart data={overview.monthlyFinancialFlow} /></div>
        <div className="lg:col-span-2"><SpendingPieChart data={overview.spendingByCategory} /></div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-4">
        <TransactionHistory rows={overview.transactionHistory} />
        <SpendingHighlights highlights={overview.spendingHighlights} />
      </div>
    </div>
  );
}
