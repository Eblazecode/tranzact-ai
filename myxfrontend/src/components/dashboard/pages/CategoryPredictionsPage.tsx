import { useEffect, useMemo, useState } from "react";
import { ChevronDown } from "lucide-react";
import { useDashboardData } from "@/lib/DashboardContext";
import { BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { api, type CategoryPredictionResponse } from "@/lib/api";
import { buildPredictionMonthOptions } from "@/lib/predictionMonths";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
const fmtShort = (v: number) => `\u20A6${(Math.abs(v) / 1000).toFixed(0)}k`;

function CategoryBlock({ cat }: { cat: CategoryPredictionResponse["categories"][number] }) {
  const [open, setOpen] = useState(true);
  const errorDirection = cat.actualSpend != null
    ? (cat.aiForecast > cat.actualSpend ? "OVER" : "UNDER")
    : null;
  return (
    <div className="bg-card border border-border rounded-xl mb-4 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-muted/30 transition-colors duration-150"
      >
        <div className="text-left">
          <p className="text-[13px] text-muted-foreground">Category</p>
          <p className="text-base font-bold text-card-foreground">{cat.categoryName}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-[11px] text-muted-foreground">Predicted Spend</p>
            <p className="text-lg font-bold text-primary">{fmt(cat.predictedSpend)}</p>
          </div>
          <ChevronDown className={`h-5 w-5 text-muted-foreground transition-transform duration-200 ${open ? "" : "-rotate-90"}`} />
        </div>
      </button>
      {open && (
        <div className="px-5 pb-5 border-t border-border pt-4">
          {/* 5-column summary row matching backend output */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
            <div className="bg-muted/30 rounded-lg p-3">
              <p className="text-[11px] text-muted-foreground">Starting Baseline</p>
              <p className="text-sm font-bold text-card-foreground mt-1">{fmt(cat.startingBaseline)}</p>
            </div>
            <div className="bg-muted/30 rounded-lg p-3">
              <p className="text-[11px] text-muted-foreground">AI Forecast</p>
              <p className="text-sm font-bold text-primary mt-1">{fmt(cat.aiForecast)}</p>
            </div>
            <div className="bg-muted/30 rounded-lg p-3">
              <p className="text-[11px] text-muted-foreground">Actual Spend</p>
              <p className="text-sm font-bold text-card-foreground mt-1">{cat.actualSpend != null ? fmt(cat.actualSpend) : "—"}</p>
            </div>
            <div className="bg-muted/30 rounded-lg p-3">
              <p className="text-[11px] text-muted-foreground">Forecast Error</p>
              <p className={`text-sm font-bold mt-1 ${errorDirection === "OVER" ? "text-destructive" : "text-green-500"}`}>
                {fmt(cat.forecastError)}{errorDirection ? ` ${errorDirection}` : ""}
              </p>
            </div>
            <div className="bg-muted/30 rounded-lg p-3">
              <p className="text-[11px] text-muted-foreground">Last Known Month</p>
              <p className="text-sm font-bold text-card-foreground mt-1">{cat.lastKnownMonth}</p>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="border-l-[3px] border-l-green-500 pl-4 py-2">
              <p className="text-[13px] text-muted-foreground mb-4">Top 3 Factors Pushing UP</p>
              <ul className="space-y-4">
                {cat.topUpFactors.map((f) => (
                  <li key={f.label} className="flex items-start justify-between gap-4 text-sm">
                    <span className="text-card-foreground leading-relaxed flex-1">{f.label}</span>
                    <span className="font-semibold text-green-500 whitespace-nowrap">+{fmt(Math.abs(f.value))}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="border-l-[3px] border-l-destructive pl-4 py-2">
              <p className="text-[13px] text-muted-foreground mb-4">Top 3 Factors Pulling DOWN</p>
              <ul className="space-y-4">
                {cat.topDownFactors.map((f) => (
                  <li key={f.label} className="flex items-start justify-between gap-4 text-sm">
                    <span className="text-card-foreground leading-relaxed flex-1">{f.label}</span>
                    <span className="font-semibold text-destructive whitespace-nowrap">−{fmt(Math.abs(f.value))}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <p className="text-[13px] text-muted-foreground mb-3">SHAP Waterfall</p>
          <ResponsiveContainer width="100%" height={cat.shapWaterfall.length * 36 + 30}>
            <BarChart data={cat.shapWaterfall} layout="vertical" margin={{ left: 10, right: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis type="number" tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
              <YAxis dataKey="label" type="category" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} width={200} />
              <Tooltip content={({ active, payload }: any) => active && payload?.[0] ? (
                <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                  <p className="text-card-foreground">{payload[0].payload.label}</p>
                  <p className="font-semibold text-card-foreground">{payload[0].payload.direction === "up" ? "+" : ""}{fmt(payload[0].value)}</p>
                </div>
              ) : null} />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {cat.shapWaterfall.map((f, i) => (
                  <Cell key={i} fill={f.direction === "up" ? "#22c55e" : "var(--destructive)"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export function CategoryPredictionsPage() {
  const { userName, startDate, endDate } = useDashboardData();
  const monthOptions = useMemo(() => buildPredictionMonthOptions(startDate, endDate), [startDate, endDate]);
  const [selectedMonth, setSelectedMonth] = useState("");
  const [prediction, setPrediction] = useState<CategoryPredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedMonth && monthOptions.length > 0) {
      setSelectedMonth(monthOptions[monthOptions.length - 1].value);
    }
  }, [monthOptions, selectedMonth]);

  useEffect(() => {
    const option = monthOptions.find((item) => item.value === selectedMonth);
    if (!option) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    api.getCategoryPrediction(userName, option.year, option.month)
      .then((payload) => {
        if (cancelled) return;
        setPrediction(payload);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to load category prediction.");
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [monthOptions, selectedMonth, userName]);

  const categories = prediction?.categories ?? [];

  return (
    <div>
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between mb-6">
        <div>
          <p className="text-[13px] text-muted-foreground">Category-wise Prediction & XAI</p>
          <p className="text-sm text-card-foreground mt-1">
            {categories.length > 0 ? `Forecast for ${categories[0].predictMonthLabel}` : "Choose a month to run the prediction"}
          </p>
        </div>
        <div className="w-full md:w-[280px]">
          <p className="text-[11px] text-muted-foreground mb-2">Filter By Month</p>
          <Select value={selectedMonth} onValueChange={setSelectedMonth}>
            <SelectTrigger className="bg-card">
              <SelectValue placeholder="Select month" />
            </SelectTrigger>
            <SelectContent>
              {monthOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {loading ? (
        <div className="bg-card border border-border rounded-xl p-5 mb-6 text-sm text-muted-foreground">
          Loading category predictions...
        </div>
      ) : null}

      {error ? (
        <div className="bg-destructive/10 border border-destructive/20 rounded-xl p-5 mb-6 text-sm text-destructive">
          {error}
        </div>
      ) : null}

      {categories.length > 0 ? (
        categories.map((cat) => (
          <CategoryBlock key={cat.categoryName} cat={cat} />
        ))
      ) : !loading ? (
        <div className="bg-card border border-border rounded-xl p-5 mb-4">
          <p className="text-sm font-semibold text-card-foreground mb-2">Category prediction is getting ready</p>
          <p className="text-sm text-muted-foreground leading-relaxed">
            The uploaded dataset does not yet have enough category history for the model, so this section will show once more monthly data is available.
          </p>
        </div>
      ) : null}

      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 mt-4">
        <p className="text-sm text-card-foreground leading-relaxed">
          Category predictions are estimates based on your historical spending patterns. Actual spending may vary.
        </p>
      </div>
    </div>
  );
}
