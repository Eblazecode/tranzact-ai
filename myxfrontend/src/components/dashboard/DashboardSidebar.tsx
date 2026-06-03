import { useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import {
  Sparkles, ChevronDown, BarChart3, PieChart, Heart, TrendingUp,
  Brain, Search, Users, AlertTriangle, LineChart, Repeat, Lightbulb, Settings,
  LogOut, Activity, Target, LayoutDashboard, History,
} from "lucide-react";
import { clearSession } from "@/lib/auth";
import type { DashboardSection } from "@/lib/dashboardSections";

const insightItems = [
  { label: "Full Spending Analysis", icon: BarChart3 },
  { label: "Detailed Category Breakdown", icon: PieChart },
  { label: "Financial Health Summary", icon: Heart },
  { label: "Monthly Financial Flow & Savings Rate", icon: TrendingUp },
  { label: "Spending Behaviour Patterns", icon: Brain },
  { label: "Financial Leakage", icon: Search },
  { label: "Filtered Pie Chart", icon: PieChart },
  { label: "Who You Send Money To", icon: Users },
  { label: "Anomaly Detection", icon: AlertTriangle },
  { label: "Balance Trajectory", icon: LineChart },
  { label: "Recurring Transactions", icon: Repeat },
];

const predictionItems = [
  { label: "Monthly Predictions & XAI", icon: Activity },
  { label: "Category Predictions & XAI", icon: Target },
];

interface SidebarSectionProps {
  title: string;
  items: { label: DashboardSection; icon: React.ElementType }[];
  activeItem: DashboardSection;
  onSelect: (label: DashboardSection) => void;
}

function SidebarSection({ title, items, activeItem, onSelect }: SidebarSectionProps) {
  const [open, setOpen] = useState(true);

  return (
    <div className="mb-2">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full px-4 py-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground hover:text-sidebar-foreground transition-colors duration-150"
      >
        {title}
        <ChevronDown
          className={`h-3.5 w-3.5 transition-transform duration-200 ${open ? "" : "-rotate-90"}`}
        />
      </button>
      <div
        className="overflow-hidden transition-all duration-300 ease-in-out"
        style={{ maxHeight: open ? `${items.length * 44}px` : "0px" }}
      >
        {items.map((item) => {
          const isActive = activeItem === item.label;
          return (
            <button
              key={item.label}
              onClick={() => onSelect(item.label)}
              className={`flex items-center gap-3 w-full px-4 py-2.5 text-sm transition-all duration-150 ${
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground border-l-[3px] border-sidebar-primary"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground border-l-[3px] border-transparent"
              }`}
            >
              <item.icon className="h-4 w-4 flex-shrink-0" />
              <span className="truncate">{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

interface DashboardSidebarProps {
  activeItem: DashboardSection;
  onSelect: (item: DashboardSection) => void;
  userName: string;
  userInitials: string;
}

export function DashboardSidebar({ activeItem, onSelect, userName, userInitials }: DashboardSidebarProps) {
  const navigate = useNavigate();

  const handleLogout = () => {
    clearSession();
    navigate({ to: "/login" });
  };

  return (
    <aside className="w-[260px] h-screen fixed left-0 top-0 bg-sidebar border-r border-border flex flex-col overflow-hidden">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-border">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="h-5 w-5 text-primary" />
          <span className="text-lg font-bold text-sidebar-foreground">
            Transac<span className="text-primary">AI</span>
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold flex-shrink-0">
            {userInitials}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-sidebar-foreground truncate">{userName}</p>
            <p className="text-xs text-muted-foreground">Personal Account</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3">
        <div className="px-4 pb-3">
          <button
            onClick={() => onSelect("Dashboard")}
            className={`flex items-center gap-3 w-full px-4 py-2.5 text-sm rounded-md transition-all duration-150 ${
              activeItem === "Dashboard"
                ? "bg-primary text-primary-foreground font-semibold shadow-sm"
                : "text-sidebar-foreground bg-sidebar-accent/50 hover:bg-sidebar-accent"
            }`}
          >
            <LayoutDashboard className="h-4 w-4" />
            Dashboard
          </button>
        </div>
        <SidebarSection title="Your Insights" items={insightItems} activeItem={activeItem} onSelect={onSelect} />
        <SidebarSection title="Predictions" items={predictionItems} activeItem={activeItem} onSelect={onSelect} />
        <div className="px-4 py-2">
          <button
            onClick={() => onSelect("Previous Uploads")}
            className={`flex items-center gap-3 w-full px-4 py-2.5 text-sm rounded-md transition-all duration-150 ${
              activeItem === "Previous Uploads"
                ? "bg-sidebar-accent text-sidebar-accent-foreground"
                : "text-sidebar-foreground hover:bg-sidebar-accent"
            }`}
          >
            <History className="h-4 w-4" />
            Previous Uploads
          </button>
        </div>
        <div className="px-4 py-2">
          <button
            onClick={() => onSelect("Recommendations")}
            className={`flex items-center gap-3 w-full px-4 py-2.5 text-sm rounded-md transition-all duration-150 ${
              activeItem === "Recommendations"
                ? "bg-sidebar-accent text-sidebar-accent-foreground"
                : "text-sidebar-foreground hover:bg-sidebar-accent"
            }`}
          >
            <Lightbulb className="h-4 w-4" />
            Recommendations
          </button>
        </div>
      </nav>

      {/* Bottom */}
      <div className="border-t border-border p-3 space-y-1">
        <button className="flex items-center gap-3 w-full px-4 py-2 text-sm text-sidebar-foreground hover:bg-sidebar-accent rounded-md transition-colors duration-150">
          <Settings className="h-4 w-4" /> Settings
        </button>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-4 py-2 text-sm text-sidebar-foreground hover:bg-sidebar-accent rounded-md transition-colors duration-150"
        >
          <LogOut className="h-4 w-4" /> Logout
        </button>
      </div>
    </aside>
  );
}
