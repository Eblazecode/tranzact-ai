from math import isnan

import pandas as pd

from utils.data_loader import load_user_dataframe
from utils.health_score import compute_health_score


DAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

LEAKAGE_CATEGORIES = {"Betting", "Charges", "SMS Charges", "Card Maintenance", "Tax"}
PRODUCTIVE_CATEGORIES = {"Savings", "Data Purchase", "Airtime", "Airtime/Data", "Electricity", "School", "Bills"}


def _round(value: float, digits: int = 2) -> float:
    if value is None:
        return 0.0
    numeric = float(value)
    if isnan(numeric):
        return 0.0
    return round(numeric, digits)


def _format_month(period_value: str) -> str:
    parsed = pd.Period(period_value, freq="M").to_timestamp()
    return parsed.strftime("%b %y")


def _health_narrative(status: str, rate: float, top_category: str) -> str:
    if status in ("EXCELLENT", "Healthy"):
        return (
            f"Your inflows are comfortably ahead of your outflows and your savings rate is {rate:.1f}%. "
            f"You still spend most heavily in {top_category}, so keeping that category intentional will protect this margin."
        )
    if status in ("MODERATE", "Moderate"):
        return (
            f"Your finances are stable, but the savings rate of {rate:.1f}% leaves only a moderate buffer. "
            f"The biggest spending pressure is currently {top_category}."
        )
    if status in ("AT RISK", "At Risk"):
        return (
            f"Your savings rate is only {rate:.1f}%, which means you are close to break-even. "
            f"Small increases in {top_category} or a drop in income could push you into overspending."
        )
    return (
        f"Your expenses are outpacing income with a savings rate of {rate:.1f}%. "
        f"Reducing pressure from {top_category} would be a strong first step."
    )


def _z_scores(series: pd.Series) -> pd.Series:
    std = series.std()
    if std == 0 or pd.isna(std):
        return pd.Series([0.0] * len(series), index=series.index)
    return (series - series.mean()) / std


def _sanitize_nan(obj):
    """Recursively replace NaN / inf floats so the payload is JSON-safe."""
    import math

    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_nan(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_sanitize_nan(v) for v in obj)
    if isinstance(obj, (int, bool, str, type(None))):
        return obj
    # pandas / numpy scalars
    try:
        val = float(obj)
        if math.isnan(val) or math.isinf(val):
            return 0.0
        return val
    except Exception:
        return str(obj)


def _safe_service_call(func, fallback, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"[WARN] Service call {func.__name__} failed: {e}")
        return fallback


def _has_monthly_prediction_content(payload: object) -> bool:
    return isinstance(payload, dict) and bool(payload.get("shapWaterfall")) and bool(payload.get("spendingDna"))


def _has_category_prediction_content(payload: object) -> bool:
    if isinstance(payload, dict):
        categories = payload.get("categories")
        return isinstance(categories, list) and len(categories) > 0
    return isinstance(payload, list) and len(payload) > 0


def get_dashboard_payload(user_name: str) -> dict[str, object]:
    # Import feature services
    from app_features.your_insights.financial_health_summary.service import get_financial_health_summary
    from app_features.your_insights.monthly_flow_and_savings_rate.service import get_monthly_flow
    from app_features.your_insights.spending_behaviour_patterns.service import get_spending_behaviour_patterns
    from app_features.your_insights.financial_leakage.service import get_financial_leakage
    from app_features.your_insights.filtered_pie_chart.service import get_filtered_pie_chart
    from app_features.your_insights.who_sends_money_to.service import get_transfers_out
    from app_features.your_insights.anomaly_detection.service import get_anomalies
    from app_features.your_insights.balance_trajectory.service import get_balance_trajectory
    from app_features.your_insights.recurring_transactions.service import get_recurring_transactions
    from app_features.predictions.monthly_prediction.service import get_monthly_prediction
    from app_features.predictions.category_prediction.service import get_category_prediction
    from app_features.recommendations.service import get_recommendations
    from app_features.recommendations.schemas import RecommendationRequest
    from app_features.predictions.monthly_prediction.schemas import MonthlyPredictionRequest
    from app_features.predictions.category_prediction.schemas import CategoryPredictionRequest

    try:
        user_df = load_user_dataframe(user_name).copy()
        user_df["YearMonth"] = user_df["Date"].dt.to_period("M")
        user_df["YearWeek"] = user_df["Date"].dt.to_period("W")
        user_df["DayOfWeek"] = user_df["Date"].dt.day_name()
        user_df["IsWeekend"] = user_df["Date"].dt.dayofweek.isin([5, 6]).astype(int)

        total_spent = float(user_df["Debit"].sum())
        total_received = float(user_df["Credit"].sum())
        net_position = total_received - total_spent

        monthly = (
            user_df.groupby("YearMonth")
            .agg(
                income=("Credit", "sum"),
                expenses=("Debit", "sum"),
                avg_balance=("Balance", "mean"),
            )
            .reset_index()
        )
        monthly["label"] = monthly["YearMonth"].astype(str).map(_format_month)
        monthly["net_savings"] = monthly["income"] - monthly["expenses"]
        monthly["rate_pct"] = monthly.apply(
            lambda row: _round((row["net_savings"] / row["income"]) * 100, 1) if row["income"] > 0 else 0.0,
            axis=1,
        )

        highest_month = monthly.loc[monthly["expenses"].idxmax()] if not monthly.empty else None
        lowest_month = monthly.loc[monthly["expenses"].idxmin()] if not monthly.empty else None

        category_summary = (
            user_df.groupby("Category")
            .agg(
                transactionCount=("Debit", "count"),
                totalSpent=("Debit", "sum"),
                avgPerTransaction=("Debit", "mean"),
                maxTransaction=("Debit", "max"),
            )
            .sort_values("totalSpent", ascending=False)
            .reset_index()
        )
        category_summary["pctOfTotal"] = category_summary["totalSpent"].apply(
            lambda value: _round((float(value) / total_spent) * 100, 1) if total_spent > 0 else 0.0
        )

        spend_by_category = [
            {"category": row["Category"], "amount": _round(row["totalSpent"])}
            for _, row in category_summary.iterrows()
        ]

        transaction_count_by_category = [
            {"category": row["Category"], "count": int(row["transactionCount"])}
            for _, row in category_summary.iterrows()
        ]

        daily_spending = (
            user_df.groupby("Date")["Debit"].sum().reset_index().sort_values("Date")
        )
        daily_spending["rolling_7"] = daily_spending["Debit"].rolling(7, min_periods=1).mean()

        spending_by_day = (
            user_df.groupby("DayOfWeek")["Debit"].sum().reindex(DAY_ORDER, fill_value=0)
        )

        top_transactions_df = user_df.nlargest(10, "Debit")[["Description", "Debit", "Date", "Category"]]
        top_transactions = [
            {
                "desc": str(row["Description"]),
                "amount": _round(row["Debit"]),
                "date": row["Date"].strftime("%Y-%m-%d"),
                "category": str(row["Category"]),
            }
            for _, row in top_transactions_df.iterrows()
        ]

        total_in, total_out = total_received, total_spent
        savings_rate = ((total_in - total_out) / total_in * 100) if total_in > 0 else 0.0
        h = compute_health_score(savings_rate, user_df)
        health_status = h["health_status"]
        top_category_name = category_summary.iloc[0]["Category"] if not category_summary.empty else "None"

        weekend_df = user_df[user_df["IsWeekend"] == 1]
        weekday_df = user_df[user_df["IsWeekend"] == 0]
        monthly_expenses = monthly["expenses"] if not monthly.empty else pd.Series(dtype=float)

        debit_only = user_df[user_df["Debit"] > 0].copy()
        size_bins = [0, 500, 2000, 10000, 50000, float("inf")]
        size_labels = ["Micro", "Small", "Medium", "Large", "Very Large"]
        size_ranges = {
            "Micro": "< N500",
            "Small": "N500 - N2,000",
            "Medium": "N2,000 - N10,000",
            "Large": "N10,000 - N50,000",
            "Very Large": "> N50,000",
        }
        debit_only["TxnSize"] = pd.cut(debit_only["Debit"], bins=size_bins, labels=size_labels)
        size_distribution = []
        for label in size_labels:
            subset = debit_only[debit_only["TxnSize"] == label]
            size_distribution.append(
                {
                    "bucket": label,
                    "range": size_ranges[label],
                    "count": int(len(subset)),
                    "total": _round(subset["Debit"].sum()),
                }
            )

        total_months = max(int(user_df["YearMonth"].nunique()), 1)
        category_consistency = (
            user_df.groupby("Category")["YearMonth"].nunique().sort_values(ascending=False)
        )

        leakage_df = user_df[user_df["Category"].isin(LEAKAGE_CATEGORIES)].copy()
        leakage_spend = float(leakage_df["Debit"].sum())
        productive_spend = float(user_df[user_df["Category"].isin(PRODUCTIVE_CATEGORIES)]["Debit"].sum())
        p2p_spend = float(user_df[user_df["Category"] == "P2P Transfer"]["Debit"].sum())
        pos_spend = float(user_df[user_df["Category"] == "POS Transaction"]["Debit"].sum())
        other_spend = max(total_spent - leakage_spend - productive_spend - p2p_spend - pos_spend, 0.0)

        leakage_breakdown = []
        for category, group in leakage_df.groupby("Category"):
            leakage_breakdown.append(
                {
                    "category": category,
                    "amount": _round(group["Debit"].sum()),
                    "count": int(len(group)),
                    "avg": _round(group["Debit"].mean()),
                }
            )

        leakage_bucket_breakdown = [
            {"bucket": "Productive", "amount": _round(productive_spend)},
            {"bucket": "Leakage", "amount": _round(leakage_spend)},
            {"bucket": "P2P Transfer", "amount": _round(p2p_spend)},
            {"bucket": "POS", "amount": _round(pos_spend)},
            {"bucket": "Other", "amount": _round(other_spend)},
        ]

        available_months = ["All", *[_format_month(str(period)) for period in user_df["YearMonth"].sort_values().unique()]]
        available_weeks = ["All", *[str(period) for period in user_df["YearWeek"].sort_values().unique()]]
        latest_month = monthly.iloc[-1]["YearMonth"] if not monthly.empty else None
        previous_month = monthly.iloc[-2]["YearMonth"] if len(monthly) > 1 else None
        latest_subset = user_df[user_df["YearMonth"] == latest_month] if latest_month is not None else user_df
        previous_subset = user_df[user_df["YearMonth"] == previous_month] if previous_month is not None else pd.DataFrame(columns=user_df.columns)

        filtered_pie_breakdown = (
            latest_subset.groupby("Category")["Debit"].sum().sort_values(ascending=False)
        )
        filtered_comparison_categories = sorted(set(latest_subset["Category"]).union(set(previous_subset["Category"])))

        monthly_pie_grid = []
        for period in user_df["YearMonth"].sort_values().unique()[-6:]:
            subset = user_df[user_df["YearMonth"] == period]
            monthly_pie_grid.append(
                {
                    "month": _format_month(str(period)),
                    "slices": [
                        {"category": category, "amount": _round(amount)}
                        for category, amount in subset.groupby("Category")["Debit"].sum().sort_values(ascending=False).items()
                    ],
                }
            )

        sent = user_df[
            (user_df["Category"] == "P2P Transfer")
            & (user_df["Description"].str.lower().str.startswith("transfer to", na=False))
        ].copy()
        sent["Recipient"] = sent["Description"].str.replace(r"^Transfer to\s+", "", regex=True).str.strip()
        recipient_summary = (
            sent.groupby("Recipient")
            .agg(frequency=("Debit", "count"), totalSent=("Debit", "sum"))
            .sort_values(["frequency", "totalSent"], ascending=[False, False])
            .reset_index()
        )

        monthly_anomaly = (
            user_df.groupby("YearMonth")["Debit"].sum().reset_index(name="amount")
        )
        monthly_anomaly["zScore"] = _z_scores(monthly_anomaly["amount"])
        weekly_anomaly = (
            user_df.groupby("YearWeek")["Debit"].sum().reset_index(name="amount")
        )
        weekly_anomaly["zScore"] = _z_scores(weekly_anomaly["amount"])

        daily_closing = user_df.groupby(user_df["Date"].dt.date).tail(1)[["Date", "Balance"]].sort_values("Date")
        rolling_30 = daily_closing.copy()
        rolling_30["rolling"] = rolling_30["Balance"].rolling(30, min_periods=1).mean()
        monthly_avg_balance = (
            user_df.groupby("YearMonth")["Balance"].mean().reset_index(name="avgBalance")
        )
        monthly_avg_balance["change"] = monthly_avg_balance["avgBalance"].diff().fillna(0)

        cleaned_descriptions = user_df.copy()
        cleaned_descriptions["CleanDescription"] = (
            cleaned_descriptions["Description"]
            .astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )
        recurring_grouped = (
            cleaned_descriptions.groupby("CleanDescription")
            .agg(
                monthsRepeated=("YearMonth", "nunique"),
                avgAmount=("Debit", "mean"),
            )
            .reset_index()
        )
        recurring_grouped["frequencyPct"] = recurring_grouped["monthsRepeated"].apply(
            lambda count: _round((count / total_months) * 100, 1)
        )
        recurring_grouped = recurring_grouped[recurring_grouped["monthsRepeated"] >= 3].sort_values(
            ["monthsRepeated", "avgAmount"], ascending=[False, False]
        )

        forecast_amount = _round(monthly["expenses"].tail(3).mean()) if not monthly.empty else 0.0
        baseline_amount = _round(monthly["expenses"].tail(1).mean()) if not monthly.empty else 0.0
        last_known_month = monthly.iloc[-1]["label"] if not monthly.empty else ""

        top_income_factor = {"label": "Recent monthly income", "value": _round(total_received / max(len(monthly), 1), 2)}
        top_spend_factor = {"label": "Recent spending average", "value": _round(monthly["expenses"].tail(3).mean() if not monthly.empty else 0, 2)}
        top_balance_factor = {"label": "Average balance", "value": _round(user_df["Balance"].mean())}

        category_prediction_rows = []
        for _, row in category_summary.head(5).iterrows():
            predicted = _round(float(row["totalSpent"]) / max(len(monthly), 1))
            category_prediction_rows.append(
                {
                    "categoryName": row["Category"],
                    "predictedSpend": predicted,
                    "startingBaseline": _round(predicted * 0.82),
                    "aiForecast": predicted,
                    "actualSpend": None,
                    "forecastError": 0,
                    "lastKnownMonth": last_known_month,
                    "topUpFactors": [
                        {"label": "Recent category average", "value": _round(predicted * 0.22)},
                        {"label": "Income support", "value": _round(top_income_factor["value"] * 0.02)},
                        {"label": "Transaction frequency", "value": _round(float(row["transactionCount"]))},
                    ],
                    "topDownFactors": [
                        {"label": "Last month normalization", "value": _round(-predicted * 0.12)},
                        {"label": "Balance restraint", "value": _round(-top_balance_factor["value"] * 0.003)},
                        {"label": "Budget pressure", "value": _round(-predicted * 0.05)},
                    ],
                    "shapWaterfall": [
                        {"label": "Recent category average", "value": _round(predicted * 0.22), "direction": "up"},
                        {"label": "Last month normalization", "value": _round(predicted * 0.12), "direction": "down"},
                        {"label": "Income support", "value": _round(top_income_factor["value"] * 0.02), "direction": "up"},
                    ],
                }
            )

        recommendation_cards = [
            {
                "id": "r1",
                "number": 1,
                "text": f"Keep your strongest attention on {top_category_name}, because it currently drives the largest share of spending.",
            },
            {
                "id": "r2",
                "number": 2,
                "text": f"Your savings rate is {savings_rate:.1f}%. Protect that margin by keeping monthly fixed costs below your current average of N{_round(monthly['expenses'].mean() if not monthly.empty else 0):,.2f}.",
            },
            {
                "id": "r3",
                "number": 3,
                "text": f"Leakage-related spending is N{_round(leakage_spend):,.2f}. Review small recurring charges before they silently compound.",
            },
            {
                "id": "r4",
                "number": 4,
                "text": "Use the monthly flow chart to spot months where income drops while discretionary transfers remain high, then adjust early.",
            },
        ]

        monthly_flow_fallback = {
            "monthly": [
                {
                    "month": row["label"],
                    "income": _round(row["income"]),
                    "expenses": _round(row["expenses"]),
                    "savings": _round(row["net_savings"]),
                    "savingsRate": _round(row["rate_pct"], 1),
                    "savingsDirection": "positive" if float(row["net_savings"]) >= 0 else "negative",
                }
                for _, row in monthly.iterrows()
            ],
            "thresholdExplanation": (
                "A healthy savings rate is typically 20% or higher. Values above 0% "
                "mean income still exceeds expenses, while values below 0% indicate overspending."
            ),
            "healthyThresholdNote": "Healthy threshold: >= 20%",
        }
        behaviour_fallback = {
            "weekendTotal": _round(weekend_df["Debit"].sum()),
            "weekdayTotal": _round(weekday_df["Debit"].sum()),
            "weekendAvg": _round(weekend_df["Debit"].mean() if not weekend_df.empty else 0),
            "weekdayAvg": _round(weekday_df["Debit"].mean() if not weekday_df.empty else 0),
            "mostExpensiveMonth": {
                "month": highest_month["label"] if highest_month is not None else "",
                "amount": _round(highest_month["expenses"]) if highest_month is not None else 0.0,
            },
            "cheapestMonth": {
                "month": lowest_month["label"] if lowest_month is not None else "",
                "amount": _round(lowest_month["expenses"]) if lowest_month is not None else 0.0,
            },
            "avgMonthlySpend": _round(monthly_expenses.mean() if not monthly.empty else 0),
            "stdDeviation": _round(monthly_expenses.std() if len(monthly_expenses) > 1 else 0),
            "sizeDistribution": size_distribution,
            "categoryConsistency": [
                {
                    "category": category,
                    "consistencyPct": _round((months / total_months) * 100, 1),
                }
                for category, months in category_consistency.items()
            ],
            "spendingByDayOfWeek": [
                {"day": day[:3], "amount": _round(amount)}
                for day, amount in spending_by_day.items()
            ],
        }
        leakage_fallback = {
            "totalLeakageAmount": _round(leakage_spend),
            "leakagePct": _round((leakage_spend / total_spent) * 100, 1) if total_spent > 0 else 0.0,
            "leakageTransactionCount": int(len(leakage_df)),
            "breakdown": leakage_breakdown,
            "bucketBreakdown": leakage_bucket_breakdown,
            "amountByCategory": [
                {"category": item["category"], "amount": item["amount"]}
                for item in leakage_breakdown
            ],
        }
        filtered_pie_fallback = {
            "availableMonths": available_months,
            "availableWeeks": available_weeks,
            "categoryBreakdown": [
                {"category": category, "amount": _round(amount)}
                for category, amount in filtered_pie_breakdown.items()
            ],
            "comparisonBreakdown": [
                {
                    "category": category,
                    "current": _round(
                        latest_subset.groupby("Category")["Debit"].sum().get(category, 0)
                    ),
                    "previous": _round(
                        previous_subset.groupby("Category")["Debit"].sum().get(category, 0)
                    ),
                }
                for category in filtered_comparison_categories
            ],
            "monthlyPieGrid": monthly_pie_grid,
        }
        recipients_fallback = {
            "availableMonths": available_months,
            "availableWeeks": available_weeks,
            "availableYears": ["All", *[str(year) for year in sorted(user_df["Date"].dt.year.unique())]],
            "table": [
                {
                    "name": row["Recipient"],
                    "frequency": int(row["frequency"]),
                    "totalSent": _round(row["totalSent"]),
                }
                for _, row in recipient_summary.iterrows()
            ],
            "transferCountByRecipient": [
                {"name": row["Recipient"], "count": int(row["frequency"])}
                for _, row in recipient_summary.iterrows()
            ],
            "amountSentByRecipient": [
                {"name": row["Recipient"], "amount": _round(row["totalSent"])}
                for _, row in recipient_summary.iterrows()
            ],
        }
        anomaly_fallback = {
            "flaggedMonths": [
                {
                    "month": str(row["YearMonth"]),
                    "zScore": _round(row["zScore"], 3),
                    "amount": _round(row["amount"]),
                }
                for _, row in monthly_anomaly[monthly_anomaly["zScore"].abs() > 2].iterrows()
            ],
            "flaggedWeeks": [
                {
                    "week": str(row["YearWeek"]),
                    "zScore": _round(row["zScore"], 3),
                    "amount": _round(row["amount"]),
                }
                for _, row in weekly_anomaly[weekly_anomaly["zScore"].abs() > 2].iterrows()
            ],
            "monthlySeries": [
                {
                    "month": str(row["YearMonth"]),
                    "amount": _round(row["amount"]),
                    "isAnomaly": bool(abs(float(row["zScore"])) > 2),
                }
                for _, row in monthly_anomaly.iterrows()
            ],
            "weeklySeries": [
                {
                    "week": str(row["YearWeek"]),
                    "amount": _round(row["amount"]),
                    "isAnomaly": bool(abs(float(row["zScore"])) > 2),
                }
                for _, row in weekly_anomaly.iterrows()
            ],
        }
        balance_fallback = {
            "startingBalance": _round(daily_closing.iloc[0]["Balance"]) if not daily_closing.empty else 0.0,
            "endingBalance": _round(daily_closing.iloc[-1]["Balance"]) if not daily_closing.empty else 0.0,
            "peakBalance": {
                "amount": _round(daily_closing["Balance"].max()) if not daily_closing.empty else 0.0,
                "date": daily_closing.loc[daily_closing["Balance"].idxmax(), "Date"].strftime("%Y-%m-%d") if not daily_closing.empty else "",
            },
            "lowestBalance": {
                "amount": _round(daily_closing["Balance"].min()) if not daily_closing.empty else 0.0,
                "date": daily_closing.loc[daily_closing["Balance"].idxmin(), "Date"].strftime("%Y-%m-%d") if not daily_closing.empty else "",
            },
            "avgBalance": _round(user_df["Balance"].mean()),
            "dangerZoneDays": int((user_df["Balance"] < 1000).sum()),
            "dailyClosing": [
                {"date": row["Date"].strftime("%Y-%m-%d"), "balance": _round(row["Balance"])}
                for _, row in daily_closing.iterrows()
            ],
            "rolling30Day": [
                {"date": row["Date"].strftime("%Y-%m-%d"), "balance": _round(row["rolling"])}
                for _, row in rolling_30.iterrows()
            ],
            "monthlyAverage": [
                {"month": _format_month(str(row["YearMonth"])), "avgBalance": _round(row["avgBalance"])}
                for _, row in monthly_avg_balance.iterrows()
            ],
            "monthOverMonthChange": [
                {"month": _format_month(str(row["YearMonth"])), "change": _round(row["change"])}
                for _, row in monthly_avg_balance.iterrows()
            ],
        }
        recurring_fallback = {
            "rows": [
                {
                    "description": str(row["CleanDescription"]).title(),
                    "frequencyPct": _round(row["frequencyPct"], 1),
                    "monthsRepeated": int(row["monthsRepeated"]),
                    "totalMonths": total_months,
                    "avgAmount": _round(row["avgAmount"]),
                }
                for _, row in recurring_grouped.head(15).iterrows()
            ],
            "patternSummary": (
                f"{len(recurring_grouped)} recurring transactions detected across {total_months} months. "
                "These appear in at least 3 distinct months."
            ),
        }
        monthly_prediction_fallback = {
            "startingBaseline": baseline_amount,
            "aiForecast": forecast_amount,
            "actualSpend": None,
            "forecastError": 0.0,
            "lastKnownMonth": last_known_month,
            "forecastAmount": forecast_amount,
            "baselineAmount": baseline_amount,
            "topUpFactors": [top_income_factor, top_spend_factor],
            "topDownFactors": [
                {"label": "Average balance restraint", "value": _round(-top_balance_factor["value"] * 0.01)},
            ],
            "shapWaterfall": [
                {"label": top_income_factor["label"], "value": top_income_factor["value"], "direction": "up"},
                {"label": top_spend_factor["label"], "value": top_spend_factor["value"], "direction": "up"},
                {"label": top_balance_factor["label"], "value": _round(-top_balance_factor["value"] * 0.01), "direction": "down"},
            ],
            "spendingDna": [
                {"label": top_income_factor["label"], "importance": top_income_factor["value"]},
                {"label": top_spend_factor["label"], "importance": top_spend_factor["value"]},
                {"label": top_balance_factor["label"], "importance": top_balance_factor["value"]},
            ],
        }
        recommendations_fallback = {
            "user": user_name,
            "healthScore": h["health_score"],
            "healthScoreMax": 85,
            "riskStatus": (
                "HEALTHY" if health_status in ("EXCELLENT", "Healthy")
                else "MODERATE" if health_status in ("MODERATE", "Moderate")
                else "AT RISK" if health_status in ("AT RISK", "At Risk")
                else "CRITICAL"
            ),
            "totalIncome": _round(total_received),
            "totalSpending": _round(total_spent),
            "savingsRatePct": _round(savings_rate, 1),
            "leakageAmount": _round(leakage_spend),
            "leakagePct": _round((leakage_spend / total_spent) * 100, 1) if total_spent > 0 else 0.0,
            "topCategoryName": top_category_name,
            "topCategoryAmount": _round(category_summary.iloc[0]["totalSpent"]) if not category_summary.empty else 0.0,
            "topCategoryPct": _round(category_summary.iloc[0]["pctOfTotal"], 1) if not category_summary.empty else 0.0,
            "anomalyStatus": "Detected" if anomaly_fallback["flaggedMonths"] or anomaly_fallback["flaggedWeeks"] else "None detected",
            "cards": recommendation_cards,
        }

        health_data = _safe_service_call(
            get_financial_health_summary,
            {
                "totalIncome": _round(total_received),
                "totalExpenses": _round(total_spent),
                "netSavings": _round(net_position),
                "savingsRatePct": _round(savings_rate, 1),
                "healthStatus": health_status,
                "healthNarrative": _health_narrative(health_status, savings_rate, top_category_name),
                "healthScore": h["health_score"],
            },
            user_name,
        )
        monthly_flow_data = _safe_service_call(get_monthly_flow, monthly_flow_fallback, user_name)
        behaviour_data = _safe_service_call(get_spending_behaviour_patterns, behaviour_fallback, user_name)
        leakage_data = _safe_service_call(get_financial_leakage, leakage_fallback, user_name)
        filtered_pie_data = _safe_service_call(get_filtered_pie_chart, filtered_pie_fallback, user_name, "month", "all")
        recipients_data = _safe_service_call(get_transfers_out, recipients_fallback, user_name, "month", "all", 10)
        anomaly_data = _safe_service_call(get_anomalies, anomaly_fallback, user_name)
        balance_data = _safe_service_call(get_balance_trajectory, balance_fallback, user_name)
        recurring_data = _safe_service_call(get_recurring_transactions, recurring_fallback, user_name)
        
        # Prediction data (using current month)
        current_date = pd.Timestamp.now()
        monthly_pred_request = MonthlyPredictionRequest(
            user_name=user_name,
            predict_month=current_date.strftime("%B"),
            predict_month_num=current_date.month,
            predict_year=current_date.year
        )
        monthly_prediction_data = _safe_service_call(
            get_monthly_prediction,
            monthly_prediction_fallback,
            monthly_pred_request,
        )
        if not _has_monthly_prediction_content(monthly_prediction_data):
            monthly_prediction_data = monthly_prediction_fallback
        
        category_pred_request = CategoryPredictionRequest(
            user_name=user_name,
            predict_month=current_date.strftime("%B"),
            predict_month_num=current_date.month,
            predict_year=current_date.year
        )
        category_prediction_data = _safe_service_call(
            get_category_prediction,
            category_prediction_rows,
            category_pred_request,
        )
        if not _has_category_prediction_content(category_prediction_data):
            category_prediction_data = category_prediction_rows
        
        recommendation_request = RecommendationRequest(user_name=user_name)
        recommendations_data = _safe_service_call(
            get_recommendations,
            recommendations_fallback,
            recommendation_request,
        )

        return _sanitize_nan({
            "userName": user_name,
            "userInitials": "".join(part[0] for part in user_name.split()[:2]).upper(),
            "startDate": user_df["Date"].min().strftime("%Y-%m-%d"),
            "endDate": user_df["Date"].max().strftime("%Y-%m-%d"),
            "fsa": {
                "transactionCount": int(len(user_df)),
                "totalSpent": _round(total_spent),
                "totalReceived": _round(total_received),
                "netPosition": _round(net_position),
                "highestSpendingMonth": {
                    "month": highest_month["label"] if highest_month is not None else "",
                    "amount": _round(highest_month["expenses"]) if highest_month is not None else 0.0,
                },
                "lowestSpendingMonth": {
                    "month": lowest_month["label"] if lowest_month is not None else "",
                    "amount": _round(lowest_month["expenses"]) if lowest_month is not None else 0.0,
                },
                "highestBalance": {
                    "amount": _round(user_df["Balance"].max()),
                    "date": user_df.loc[user_df["Balance"].idxmax(), "Date"].strftime("%Y-%m-%d"),
                },
                "lowestBalance": {
                    "amount": _round(user_df["Balance"].min()),
                    "date": user_df.loc[user_df["Balance"].idxmin(), "Date"].strftime("%Y-%m-%d"),
                },
                "currentBalance": _round(user_df.iloc[-1]["Balance"]),
                "highestSpendingCategory": {
                    "name": top_category_name,
                    "amount": _round(category_summary.iloc[0]["totalSpent"]) if not category_summary.empty else 0.0,
                },
                "spendByCategory": spend_by_category,
                "monthlyIncomeVsExpenses": [
                    {
                        "month": row.get("month", ""),
                        "income": row.get("income", 0.0),
                        "expenses": row.get("expenses", row.get("expense", 0.0)),
                    }
                    for row in monthly_flow_data.get("monthly", [])
                ],
                "transactionCountByCategory": transaction_count_by_category,
                "dailySpendingTrend": [
                    {"date": row["Date"].strftime("%Y-%m-%d"), "amount": _round(row["Debit"])}
                    for _, row in daily_spending.iterrows()
                ],
                "spendingByDayOfWeek": behaviour_data.get(
                    "spendingByDayOfWeek",
                    [{"day": day[:3], "amount": _round(amount)} for day, amount in spending_by_day.items()],
                ),
                "top10LargestTransactions": top_transactions,
                "dateRangeText": f"Statement covers transactions from {user_df['Date'].min().strftime('%Y-%m-%d')} to {user_df['Date'].max().strftime('%Y-%m-%d')}.",
                "summaryNotes": f"Income exceeds expenses for this user, with {top_category_name} leading total spending across the analysed period.",
            },
            "categoryBreakdown": {
                "rows": [
                    {
                        "category": row["Category"],
                        "transactionCount": int(row["transactionCount"]),
                        "totalSpent": _round(row["totalSpent"]),
                        "avgPerTransaction": _round(row["avgPerTransaction"]),
                        "maxTransaction": _round(row["maxTransaction"]),
                        "pctOfTotal": _round(row["pctOfTotal"], 1),
                    }
                    for _, row in category_summary.iterrows()
                ],
                "avgDailySpend": _round(daily_spending["Debit"].mean() if not daily_spending.empty else 0),
                "avgMonthlySpend": _round(monthly["expenses"].mean() if not monthly.empty else 0),
                "mostActiveCategory": top_category_name,
            },
            "health": health_data,
            "monthlyFlow": monthly_flow_data,
            "behaviour": behaviour_data,
            "leakage": leakage_data,
            "filteredPie": filtered_pie_data,
            "recipients": recipients_data,
            "anomaly": anomaly_data,
            "balance": balance_data,
            "recurring": recurring_data,
            "monthlyPredictionXai": monthly_prediction_data,
            "categoryPredictionXai": category_prediction_data,
            "aiRecommendations": recommendations_data,
        })
    except Exception as e:
        # Fallback with basic data if services fail
        return _sanitize_nan({
            "userName": user_name,
            "userInitials": "".join(part[0] for part in user_name.split()[:2]).upper(),
            "error": f"Service integration error: {str(e)}"
        })
