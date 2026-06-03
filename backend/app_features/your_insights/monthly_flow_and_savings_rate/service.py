from utils.data_loader import load_user_dataframe


def get_monthly_flow(user_name: str) -> dict[str, list[dict[str, float | str]] | str]:
    user_df = load_user_dataframe(user_name)
    monthly = (
        user_df.groupby(user_df["Date"].dt.to_period("M"))
        .agg(
            Income=("Credit", "sum"),
            Expense=("Debit", "sum"),
        )
        .reset_index()
    )
    monthly["Savings"] = monthly["Income"] - monthly["Expense"]
    monthly["Savings_Rate"] = monthly.apply(
        lambda row: round((row["Savings"] / row["Income"]) * 100, 1) if row["Income"] > 0 else 0.0,
        axis=1,
    )
    monthly["Date"] = monthly["Date"].astype(str)

    points = [
        {
            "month": row["Date"],
            "income": round(float(row["Income"]), 2),
            "expenses": round(float(row["Expense"]), 2),
            "savings": round(float(row["Savings"]), 2),
            "savingsRate": round(float(row["Savings_Rate"]), 2),
            "savingsDirection": "positive" if float(row["Savings"]) >= 0 else "negative",
        }
        for _, row in monthly.iterrows()
    ]

    return {
        "monthly": points,
        "thresholdExplanation": (
            "A healthy savings rate is typically 20% or higher. Values above 0% "
            "mean income still exceeds expenses, while values below 0% indicate overspending."
        ),
        "healthyThresholdNote": "Healthy threshold: >= 20%",
    }
