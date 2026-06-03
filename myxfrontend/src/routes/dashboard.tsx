import { Outlet, createFileRoute, redirect } from "@tanstack/react-router";
import { canUseBrowserSession, isAuthenticated } from "@/lib/auth";

export const Route = createFileRoute("/dashboard")({
  beforeLoad: () => {
    if (!canUseBrowserSession()) {
      return;
    }
    if (!isAuthenticated()) {
      throw redirect({ to: "/login" });
    }
  },
  head: () => ({
    meta: [
      { title: "Dashboard - TransacAI" },
      { name: "description", content: "Your TransacAI financial intelligence dashboard." },
    ],
  }),
  component: DashboardRouteView,
});

function DashboardRouteView() {
  return <Outlet />;
}
