import { createContext, useContext } from "react";
import type { DashboardData } from "./dashboardData";

const DashboardContext = createContext<DashboardData | null>(null);

interface DashboardProviderProps {
  data: DashboardData;
  children: React.ReactNode;
}

export function DashboardProvider({ data, children }: DashboardProviderProps) {
  return (
    <DashboardContext.Provider value={data}>
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboardData(): DashboardData {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error("useDashboardData must be used within DashboardProvider");
  return ctx;
}

export function useDashboardLoading() {
  return { loading: true, error: null };
}
