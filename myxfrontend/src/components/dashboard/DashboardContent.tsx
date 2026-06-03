import { useEffect, useState } from "react";
import { Moon, Sun, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { UploadModal } from "./UploadModal";
import { FullSpendingAnalysisPage } from "./pages/FullSpendingAnalysisPage";
import { CategoryBreakdownPage } from "./pages/CategoryBreakdownPage";
import { FinancialHealthPage } from "./pages/FinancialHealthPage";
import { MonthlyFlowSavingsPage } from "./pages/MonthlyFlowSavingsPage";
import { SpendingBehaviourPage } from "./pages/SpendingBehaviourPage";
import { FinancialLeakagePage } from "./pages/FinancialLeakagePage";
import { FilteredPieChartPage } from "./pages/FilteredPieChartPage";
import { RecipientsPage } from "./pages/RecipientsPage";
import { AnomalyDetectionPage } from "./pages/AnomalyDetectionPage";
import { BalanceTrajectoryPage } from "./pages/BalanceTrajectoryPage";
import { RecurringTransactionsPage } from "./pages/RecurringTransactionsPage";
import { MonthlyPredictionsPage } from "./pages/MonthlyPredictionsPage";
import { CategoryPredictionsPage } from "./pages/CategoryPredictionsPage";
import { PreviousUploadsPage } from "./pages/PreviousUploadsPage";
import { RecommendationsPage } from "./pages/RecommendationsPage";
import { DashboardOverview } from "./DashboardOverview";
import { useDashboardData } from "@/lib/DashboardContext";
import { getCurrentUserName } from "@/lib/auth";
import type { DashboardSection } from "@/lib/dashboardSections";

function ThemeToggle() {
  const [dark, setDark] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("theme") === "dark" || document.documentElement.classList.contains("dark");
    }
    return false;
  });

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [dark]);

  return (
    <button
      onClick={() => setDark(!dark)}
      className="p-2 rounded-lg bg-muted hover:bg-muted/80 transition-all duration-200"
      aria-label="Toggle theme"
    >
      <div className="transition-transform duration-200" style={{ transform: dark ? "rotate(180deg)" : "rotate(0deg)" }}>
        {dark ? <Sun className="h-4 w-4 text-foreground" /> : <Moon className="h-4 w-4 text-foreground" />}
      </div>
    </button>
  );
}

interface DashboardContentProps {
  activeItem: DashboardSection;
  onStatementProcessed?: () => void | Promise<void>;
  refreshKey?: number;
}

function getGreetingForHour(hour: number) {
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

export function DashboardContent({ activeItem, onStatementProcessed, refreshKey = 0 }: DashboardContentProps) {
  const data = useDashboardData();
  const [uploadOpen, setUploadOpen] = useState(false);
  const [currentTime, setCurrentTime] = useState(() => new Date());

  useEffect(() => {
    const timer = window.setInterval(() => {
      setCurrentTime(new Date());
    }, 60_000);

    return () => window.clearInterval(timer);
  }, []);

  const greeting = getGreetingForHour(currentTime.getHours());
  const displayName = getCurrentUserName();

  const renderPage = () => {
    switch (activeItem) {
      case "Dashboard": return <DashboardOverview refreshKey={refreshKey} />;
      case "Full Spending Analysis": return <FullSpendingAnalysisPage />;
      case "Detailed Category Breakdown": return <CategoryBreakdownPage />;
      case "Financial Health Summary": return <FinancialHealthPage />;
      case "Monthly Financial Flow & Savings Rate": return <MonthlyFlowSavingsPage />;
      case "Spending Behaviour Patterns": return <SpendingBehaviourPage />;
      case "Financial Leakage": return <FinancialLeakagePage />;
      case "Filtered Pie Chart": return <FilteredPieChartPage />;
      case "Who You Send Money To": return <RecipientsPage />;
      case "Anomaly Detection": return <AnomalyDetectionPage />;
      case "Balance Trajectory": return <BalanceTrajectoryPage />;
      case "Recurring Transactions": return <RecurringTransactionsPage />;
      case "Monthly Predictions & XAI": return <MonthlyPredictionsPage />;
      case "Category Predictions & XAI": return <CategoryPredictionsPage />;
      case "Previous Uploads": return <PreviousUploadsPage onUploadSelected={onStatementProcessed} />;
      case "Recommendations": return <RecommendationsPage />;
      default: return <DashboardOverview refreshKey={refreshKey} />;
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-[1400px]">
      <div className="flex items-start justify-between mb-8 sticky top-0 bg-background/95 backdrop-blur-sm z-10 -mx-6 lg:-mx-8 px-6 lg:px-8 py-4 border-b border-border">
        <div>
          <h1 className="text-2xl font-bold text-foreground">{greeting}, {displayName}</h1>
          <p className="text-sm text-muted-foreground mt-1">Your logs span {data.startDate} to {data.endDate}</p>
        </div>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Button onClick={() => setUploadOpen(true)} className="bg-primary text-primary-foreground gap-2">
            <Upload className="h-4 w-4" /> Upload Statement
          </Button>
        </div>
      </div>

      <div key={`${activeItem}-${refreshKey}`}>
        {renderPage()}
      </div>

      <UploadModal
        open={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onProcessed={onStatementProcessed}
      />
    </div>
  );
}
