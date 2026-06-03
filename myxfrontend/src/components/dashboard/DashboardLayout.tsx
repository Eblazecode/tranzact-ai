import { startTransition, useCallback, useEffect, useState } from "react";
import { DashboardSidebar } from "./DashboardSidebar";
import { DashboardContent } from "./DashboardContent";
import { DashboardProvider } from "@/lib/DashboardContext";
import { getCurrentUserName, updateSessionUserName } from "@/lib/auth";
import { api } from "@/lib/api";
import { getEmptyDashboardData, loadDashboardData } from "@/lib/dashboardData";
import type { DashboardSection } from "@/lib/dashboardSections";

interface DashboardLayoutProps {
  activeItem: DashboardSection;
  onSelect: (item: DashboardSection) => void;
}

export function DashboardLayout({ activeItem, onSelect }: DashboardLayoutProps) {
  const [data, setData] = useState(() => getEmptyDashboardData(getCurrentUserName()));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refreshDashboardData = useCallback(async () => {
    setLoading(true);

    try {
      const currentUser = await api.getCurrentUser().catch(() => null);
      const resolvedUserName = currentUser?.first_name || getCurrentUserName();

      if (currentUser?.first_name) {
        updateSessionUserName(currentUser.first_name);
      }

      const nextData = await loadDashboardData(resolvedUserName);
      startTransition(() => {
        setData(nextData);
        setError(null);
        setRefreshKey((value) => value + 1);
        setLoading(false);
      });
    } catch (err: unknown) {
      startTransition(() => {
        setError(err instanceof Error ? err.message : "Failed to load backend data.");
        setLoading(false);
      });
    }
  }, []);

  useEffect(() => {
    void refreshDashboardData();
  }, [refreshDashboardData]);

  return (
    <DashboardProvider data={data}>
      <div className="flex min-h-screen bg-background">
        <DashboardSidebar activeItem={activeItem} onSelect={onSelect} userName={data.userName} userInitials={data.userInitials} />
        <main className="ml-[260px] flex-1 overflow-y-auto">
          {loading && (
            <div className="border-b border-border bg-primary/5 px-6 py-3 text-sm text-foreground">
              Loading live dashboard data from the backend...
            </div>
          )}
          {error && (
            <div className="border-b border-border bg-amber-500/10 px-6 py-3 text-sm text-foreground">
              Dashboard overview is using fallback data. {error?.replace(/^.*?Service integration error:.*?(\d{3}:\s*)?/,'').replace(/No preprocessed dataset found for user/,'No data found for user')}
            </div>
          )}
          <DashboardContent activeItem={activeItem} onStatementProcessed={refreshDashboardData} refreshKey={refreshKey} />
        </main>
      </div>
    </DashboardProvider>
  );
}
