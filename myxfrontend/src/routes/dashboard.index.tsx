import { createFileRoute, redirect } from "@tanstack/react-router";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { DEFAULT_DASHBOARD_SECTION, sectionToSlug } from "@/lib/dashboardSections";

export const Route = createFileRoute("/dashboard/")({
  beforeLoad: () => {
    // Redirect bare /dashboard to /dashboard/overview
    throw redirect({ to: "/dashboard/$section", params: { section: sectionToSlug(DEFAULT_DASHBOARD_SECTION) } });
  },
});
