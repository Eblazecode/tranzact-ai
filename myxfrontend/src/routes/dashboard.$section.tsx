import { createFileRoute, redirect } from "@tanstack/react-router";

import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { canUseBrowserSession, isAuthenticated } from "@/lib/auth";
import {
  DEFAULT_DASHBOARD_SECTION,
  sectionToSlug,
  slugToSection,
} from "@/lib/dashboardSections";

export const Route = createFileRoute("/dashboard/$section")({
  beforeLoad: ({ params }) => {
    if (!canUseBrowserSession()) {
      return;
    }

    if (!isAuthenticated()) {
      throw redirect({ to: "/login" });
    }

    // Validate the slug resolves to a known section
    const section = slugToSection(params.section);
    if (section === DEFAULT_DASHBOARD_SECTION && params.section !== sectionToSlug(DEFAULT_DASHBOARD_SECTION)) {
      throw redirect({ to: "/dashboard" });
    }
  },
  head: ({ params }) => ({
    meta: [
      { title: `${slugToSection(params.section)} - TransacAI` },
      { name: "description", content: "Your TransacAI financial intelligence dashboard." },
    ],
  }),
  component: DashboardSectionRouteView,
});

function DashboardSectionRouteView() {
  const params = Route.useParams();
  const navigate = Route.useNavigate();
  const activeItem = slugToSection(params.section);

  return (
    <DashboardLayout
      activeItem={activeItem}
      onSelect={(item) => {
        void navigate({
          to: "/dashboard/$section",
          params: { section: sectionToSlug(item) },
        });
      }}
    />
  );
}
