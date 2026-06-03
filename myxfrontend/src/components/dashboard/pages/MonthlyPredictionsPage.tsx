import { useEffect, useMemo, useState } from "react";
import { BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

import { useDashboardData } from "@/lib/DashboardContext";
import { api, type MonthlyPredictionResponse } from "@/lib/api";
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

function StatCard({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <p className="text-[13px] text-muted-foreground">{label}</p>
      <p className={`text-xl font-bold mt-1 ${accent ?? "text-card-foreground"}`}>{value}</p>
    </div>
  );
}

export function MonthlyPredictionsPage() {
  const { userName, startDate, endDate } = useDashboardData();
  const monthOptions = useMemo(() => buildPredictionMonthOptions(startDate, endDate), [startDate, endDate]);
  const [selectedMonth, setSelectedMonth] = useState("");
  const [prediction, setPrediction] = useState<MonthlyPredictionResponse | null>(null);
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

    api.getMonthlyPrediction(userName, option.year, option.month)
      .then((payload) => {
        if (cancelled) return;
        setPrediction(payload);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to load monthly prediction.");
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [monthOptions, selectedMonth, userName]);

  const m = prediction;
  const maxImp = m && m.spendingDna.length > 0 ? Math.max(...m.spendingDna.map((d) => d.importance)) : 1;
  const errorDirection = m?.actualSpend != null
    ? (m.aiForecast > m.actualSpend ? "OVER" : "UNDER")
    : null;
  const hasExplanation = Boolean(m && m.shapWaterfall.length > 0 && m.spendingDna.length > 0);

  return (
    <div>
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between mb-6">
        <div>
          <p className="text-[13px] text-muted-foreground">Monthly Prediction & XAI</p>
          <p className="text-sm text-card-foreground mt-1">
            {m ? `Forecast for ${m.predictMonthLabel}` : "Choose a month to run the prediction"}
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
          Loading monthly prediction...
        </div>
      ) : null}

      {error ? (
        <div className="bg-destructive/10 border border-destructive/20 rounded-xl p-5 mb-6 text-sm text-destructive">
          {error}
        </div>
      ) : null}

      {m ? (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
            <StatCard label="Starting Baseline" value={fmt(m.startingBaseline)} />
            <StatCard label="AI Forecast" value={fmt(m.aiForecast)} accent="text-primary" />
            <StatCard label="Actual Spend" value={m.actualSpend != null ? fmt(m.actualSpend) : "-"} />
            <StatCard
              label="Forecast Error"
              value={`${fmt(m.forecastError)}${errorDirection ? ` ${errorDirection}` : ""}`}
              accent={errorDirection === "OVER" ? "text-destructive" : "text-green-500"}
            />
            <StatCard label="Last Known Month" value={m.lastKnownMonth} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            <div className="bg-card border border-border rounded-xl p-6 border-l-[3px] border-l-green-500">
              <p className="text-[13px] text-muted-foreground mb-4">Top 3 Factors Pushing UP</p>
              <ul className="space-y-4">
                {m.topUpFactors.map((f) => (
                  <li key={f.label} className="flex items-start justify-between gap-4 text-sm">
                    <span className="text-card-foreground leading-relaxed flex-1">{f.label}</span>
                    <span className="font-semibold text-green-500 whitespace-nowrap">+{fmt(Math.abs(f.value))}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-card border border-border rounded-xl p-6 border-l-[3px] border-l-destructive">
              <p className="text-[13px] text-muted-foreground mb-4">Top 3 Factors Pulling DOWN</p>
              <ul className="space-y-4">
                {m.topDownFactors.map((f) => (
                  <li key={f.label} className="flex items-start justify-between gap-4 text-sm">
                    <span className="text-card-foreground leading-relaxed flex-1">{f.label}</span>
                    <span className="font-semibold text-destructive whitespace-nowrap">-{fmt(Math.abs(f.value))}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-5 mb-6">
            <p className="text-[13px] text-muted-foreground mb-1">{userName} - SHAP Explanation</p>
            <p className="text-xs text-muted-foreground mb-4">Green = pushed forecast UP . Red = pulled forecast DOWN</p>
            <div className="bg-muted/30 rounded-lg p-3 mb-4 text-sm text-card-foreground">
              Baseline {fmt(m.baselineAmount)} to Forecast {fmt(m.forecastAmount)} . Error {fmt(m.forecastError)}
            </div>
            {hasExplanation ? (
              <ResponsiveContainer width="100%" height={m.shapWaterfall.length * 36 + 30}>
                <BarChart data={m.shapWaterfall} layout="vertical" margin={{ left: 10, right: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis type="number" tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
                  <YAxis dataKey="label" type="category" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} width={220} />
                  <Tooltip content={({ active, payload }: any) => active && payload?.[0] ? (
                    <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                      <p className="text-card-foreground">{payload[0].payload.label}</p>
                      <p className="font-semibold text-card-foreground">{payload[0].payload.direction === "up" ? "+" : ""}{fmt(payload[0].value)}</p>
                    </div>
                  ) : null} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {m.shapWaterfall.map((f, i) => (
                      <Cell key={i} fill={f.direction === "up" ? "#22c55e" : "var(--destructive)"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-muted-foreground leading-relaxed">
                Monthly prediction details will appear here as soon as the uploaded statement provides enough history for the model explanation.
              </p>
            )}
          </div>

          <div className="bg-card border border-border rounded-xl p-5 mb-6">
            <p className="text-[13px] text-muted-foreground mb-1">Spending DNA - Feature Importance</p>
            <p className="text-xs text-muted-foreground mb-4">Average push the AI applies per factor across all months</p>
            {m.spendingDna.length > 0 ? (
              <ResponsiveContainer width="100%" height={m.spendingDna.length * 32 + 30}>
                <BarChart data={m.spendingDna} layout="vertical" margin={{ left: 10, right: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis type="number" tickFormatter={fmtShort} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
                  <YAxis dataKey="label" type="category" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} width={220} />
                  <Tooltip content={({ active, payload }: any) => active && payload?.[0] ? (
                    <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-sm">
                      <p className="text-card-foreground">{payload[0].payload.label}</p>
                      <p className="font-semibold text-card-foreground">avg. push: {fmt(payload[0].value)}</p>
                    </div>
                  ) : null} />
                  <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                    {m.spendingDna.map((d, i) => {
                      const intensity = d.importance / maxImp;
                      const lightness = 0.7 - intensity * 0.2;
                      const chroma = 0.15 + intensity * 0.1;
                      const hue = 30 - intensity * 15;
                      return <Cell key={i} fill={`oklch(${lightness} ${chroma} ${hue})`} />;
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-muted-foreground leading-relaxed">
                Feature-importance bars will render here once the prediction response includes model explanation data.
              </p>
            )}
          </div>
        </>
      ) : null}

      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
        <p className="text-sm text-card-foreground leading-relaxed">
          These predictions are generated by a machine learning model trained on your past transactions. Predictions are indicative and not financial guarantees.
        </p>
      </div>
    </div>
  );
}
