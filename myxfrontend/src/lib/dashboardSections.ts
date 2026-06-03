export const DASHBOARD_SECTION_LABELS = [
  "Dashboard",
  "Full Spending Analysis",
  "Detailed Category Breakdown",
  "Financial Health Summary",
  "Monthly Financial Flow & Savings Rate",
  "Spending Behaviour Patterns",
  "Financial Leakage",
  "Filtered Pie Chart",
  "Who You Send Money To",
  "Anomaly Detection",
  "Balance Trajectory",
  "Recurring Transactions",
  "Monthly Predictions & XAI",
  "Category Predictions & XAI",
  "Previous Uploads",
  "Recommendations",
] as const;

export type DashboardSection = (typeof DASHBOARD_SECTION_LABELS)[number];

export const DEFAULT_DASHBOARD_SECTION: DashboardSection = "Dashboard";

/** URL-safe slugs for each section (used in route params) */
export const SECTION_SLUGS: Record<DashboardSection, string> = {
  "Dashboard": "overview",
  "Full Spending Analysis": "full-spending-analysis",
  "Detailed Category Breakdown": "category-breakdown",
  "Financial Health Summary": "financial-health",
  "Monthly Financial Flow & Savings Rate": "monthly-flow-savings",
  "Spending Behaviour Patterns": "spending-behaviour",
  "Financial Leakage": "financial-leakage",
  "Filtered Pie Chart": "filtered-pie",
  "Who You Send Money To": "recipients",
  "Anomaly Detection": "anomaly-detection",
  "Balance Trajectory": "balance-trajectory",
  "Recurring Transactions": "recurring-transactions",
  "Monthly Predictions & XAI": "monthly-predictions-xai",
  "Category Predictions & XAI": "category-predictions-xai",
  "Previous Uploads": "previous-uploads",
  "Recommendations": "recommendations",
};

/** Reverse map: slug → DashboardSection label */
const SLUG_TO_SECTION: Record<string, DashboardSection> = Object.fromEntries(
  Object.entries(SECTION_SLUGS).map(([label, slug]) => [slug, label as DashboardSection]),
);

export function sectionToSlug(section: DashboardSection): string {
  return SECTION_SLUGS[section];
}

export function slugToSection(slug: string): DashboardSection {
  return SLUG_TO_SECTION[slug] ?? DEFAULT_DASHBOARD_SECTION;
}

export function isDashboardSection(value: string): value is DashboardSection {
  return (DASHBOARD_SECTION_LABELS as readonly string[]).includes(value);
}

export function normalizeDashboardSection(value?: string): DashboardSection {
  if (!value) return DEFAULT_DASHBOARD_SECTION;
  return isDashboardSection(value) ? value : DEFAULT_DASHBOARD_SECTION;
}
