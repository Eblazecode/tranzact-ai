from utils.data_loader import load_user_dataframe


DAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def _safe_round(value: float) -> float:
    return round(float(value), 2)


def get_detailed_category_breakdown(user_name: str) -> dict[str, object]:
    user_df = load_user_dataframe(user_name)
    user_df = user_df.sort_values("Date").copy()
    user_df["YearMonth"] = user_df["Date"].dt.to_period("M")
    user_df["DayOfWeek"] = user_df["Date"].dt.day_name()

    summary = (
        user_df.groupby("Category")
        .agg(
            Transactions=("Debit", "count"),
            Total_Spent=("Debit", "sum"),
            Avg_Per_Txn=("Debit", "mean"),
            Max_Txn=("Debit", "max"),
        )
        .sort_values("Total_Spent", ascending=False)
        .round(2)
        .reset_index()
    )

    total_spent = float(user_df["Debit"].sum())
    total_received = float(user_df["Credit"].sum())
    net_position = total_received - total_spent
    avg_daily_spend = float(user_df.groupby("Date")["Debit"].sum().mean())
    avg_monthly_spend = float(user_df.groupby("YearMonth")["Debit"].sum().mean())
    most_active = user_df["Category"].value_counts()

    if total_spent > 0:
        summary["% of Total Spend"] = (summary["Total_Spent"] / total_spent * 100).round(1)
    else:
        summary["% of Total Spend"] = 0.0

    summary_rows = [
        {
            "category": row["Category"],
            "transactions": int(row["Transactions"]),
            "total_spent": _safe_round(row["Total_Spent"]),
            "avg_per_txn": _safe_round(row["Avg_Per_Txn"]),
            "max_txn": _safe_round(row["Max_Txn"]),
            "percent_of_total_spend": round(float(row["% of Total Spend"]), 1),
        }
        for _, row in summary.iterrows()
    ]

    category_spend_chart = [
        {
            "category": row["Category"],
            "amount": _safe_round(row["Total_Spent"]),
        }
        for _, row in summary.sort_values("Total_Spent", ascending=True).iterrows()
    ]

    monthly_income_vs_expenses = (
        user_df.groupby("YearMonth")
        .agg(
            income=("Credit", "sum"),
            expense=("Debit", "sum"),
        )
        .reset_index()
    )
    monthly_income_vs_expenses["YearMonth"] = monthly_income_vs_expenses["YearMonth"].astype(str)
    monthly_income_vs_expenses_chart = [
        {
            "month": row["YearMonth"],
            "income": _safe_round(row["income"]),
            "expense": _safe_round(row["expense"]),
        }
        for _, row in monthly_income_vs_expenses.iterrows()
    ]

    category_counts = user_df["Category"].value_counts()
    top_categories = category_counts.head(7).copy()
    other_categories_count = int(category_counts.iloc[7:].sum()) if len(category_counts) > 7 else 0
    if other_categories_count > 0:
        top_categories.loc["Other Categories"] = other_categories_count
    transaction_count_by_category_chart = [
        {"category": category, "count": int(count)}
        for category, count in top_categories.items()
    ]

    daily_spending = user_df.groupby("Date")["Debit"].sum().reset_index()
    daily_spending["Rolling7"] = daily_spending["Debit"].rolling(7, min_periods=1).mean()
    daily_spending_trend_chart = [
        {
            "date": row["Date"].strftime("%Y-%m-%d"),
            "amount": _safe_round(row["Debit"]),
            "rolling_7_day_avg": _safe_round(row["Rolling7"]),
        }
        for _, row in daily_spending.iterrows()
    ]

    day_of_week_spending = (
        user_df.groupby("DayOfWeek")["Debit"]
        .sum()
        .reindex(DAY_ORDER, fill_value=0)
        .reset_index()
    )
    day_of_week_chart = [
        {
            "day": row["DayOfWeek"],
            "amount": _safe_round(row["Debit"]),
            "is_weekend": row["DayOfWeek"] in {"Saturday", "Sunday"},
        }
        for _, row in day_of_week_spending.iterrows()
    ]

    top_10_largest = user_df.nlargest(10, "Debit")[["Date", "Category", "Description", "Debit"]]
    top_10_largest_chart = [
        {
            "date": row["Date"].strftime("%Y-%m-%d"),
            "category": row["Category"],
            "description": str(row["Description"]),
            "amount": _safe_round(row["Debit"]),
        }
        for _, row in top_10_largest.iterrows()
    ]

    return {
        "summary": summary_rows,
        "totals": {
            "total_spent": _safe_round(total_spent),
            "total_received": _safe_round(total_received),
            "net_position": _safe_round(net_position),
            "avg_daily_spend": _safe_round(avg_daily_spend),
            "avg_monthly_spend": _safe_round(avg_monthly_spend),
            "most_active_category": most_active.index[0],
            "most_active_count": int(most_active.iloc[0]),
        },
        "charts": {
            "category_spend_bar": category_spend_chart,
            "monthly_income_vs_expenses": monthly_income_vs_expenses_chart,
            "transaction_count_by_category": transaction_count_by_category_chart,
            "daily_spending_trend": daily_spending_trend_chart,
            "spending_by_day_of_week": day_of_week_chart,
            "top_10_largest_transactions": top_10_largest_chart,
        },
    }
