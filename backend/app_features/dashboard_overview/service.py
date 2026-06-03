import math

import pandas as pd

from utils.data_loader import load_user_dataframe


def _round(value: float, digits: int = 2) -> float:
    if pd.isna(value):
        return 0.0
    return round(float(value), digits)


def _format_month(period_value: pd.Period | str) -> str:
    parsed = pd.Period(period_value, freq="M").to_timestamp()
    return parsed.strftime("%b %y")


def _sanitize_nan(obj):
    """Recursively replace NaN / inf floats so the payload is JSON-safe."""
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
    try:
        val = float(obj)
        if math.isnan(val) or math.isinf(val):
            return 0.0
        return val
    except Exception:
        return str(obj)


def _pct_change(current: float, previous: float) -> float:
    current = float(current or 0)
    previous = float(previous or 0)
    if previous == 0:
        return 0.0 if current == 0 else 100.0
    return round(((current - previous) / abs(previous)) * 100, 1)


def get_dashboard_overview(user_name: str) -> dict[str, object]:
    user_df = load_user_dataframe(user_name).copy()
    user_df = user_df.sort_values("Date").reset_index(drop=True)
    user_df["YearMonth"] = user_df["Date"].dt.to_period("M")
    user_df["Amount"] = user_df.apply(
        lambda row: float(row["Debit"]) if float(row["Debit"]) > 0 else float(row["Credit"]),
        axis=1,
    )

    total_credit = float(user_df["Credit"].sum())
    total_debit = float(user_df["Debit"].sum())
    net_position = total_credit - total_debit
    total_balance = float(user_df.iloc[-1]["Balance"]) if not user_df.empty else 0.0

    monthly = (
        user_df.groupby("YearMonth")
        .agg(
            income=("Credit", "sum"),
            expenses=("Debit", "sum"),
            closingBalance=("Balance", "last"),
        )
        .reset_index()
    )
    monthly["label"] = monthly["YearMonth"].astype(str).map(_format_month)
    monthly["net"] = monthly["income"] - monthly["expenses"]

    latest_month = monthly.iloc[-1] if len(monthly) >= 1 else None
    previous_month = monthly.iloc[-2] if len(monthly) >= 2 else None

    balance_change = _pct_change(
        latest_month["closingBalance"] if latest_month is not None else 0,
        previous_month["closingBalance"] if previous_month is not None else 0,
    )
    net_position_change = _pct_change(
        latest_month["net"] if latest_month is not None else 0,
        previous_month["net"] if previous_month is not None else 0,
    )
    credit_change = _pct_change(
        latest_month["income"] if latest_month is not None else 0,
        previous_month["income"] if previous_month is not None else 0,
    )
    debit_change = _pct_change(
        latest_month["expenses"] if latest_month is not None else 0,
        previous_month["expenses"] if previous_month is not None else 0,
    )

    category_spend = (
        user_df.groupby("Category")["Debit"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    transaction_history = (
        user_df.sort_values("Date", ascending=True)[["Description", "Category", "Date", "Amount"]]
        .to_dict("records")
    )

    debit_df = user_df[user_df["Debit"] > 0].sort_values("Debit", ascending=False)
    highest = debit_df.iloc[0] if not debit_df.empty else None
    lowest = debit_df.iloc[-1] if not debit_df.empty else None

    return _sanitize_nan({
        "summaryCards": [
            {"label": "Total Balance", "amount": _round(total_balance), "changePct": balance_change},
            {"label": "Net Position", "amount": _round(net_position), "changePct": net_position_change},
            {"label": "Total Credit", "amount": _round(total_credit), "changePct": credit_change},
            {"label": "Total Debit", "amount": _round(total_debit), "changePct": debit_change},
        ],
        "monthlyFinancialFlow": [
            {
                "month": row["label"],
                "income": _round(row["income"]),
                "expenses": _round(row["expenses"]),
            }
            for _, row in monthly.iterrows()
        ],
        "spendingByCategory": [
            {"category": row["Category"], "amount": _round(row["Debit"])}
            for _, row in category_spend.iterrows()
        ],
        "transactionHistory": [
            {
                "description": str(row["Description"]),
                "category": str(row["Category"]),
                "date": row["Date"].strftime("%Y-%m-%d"),
                "amount": _round(row["Amount"]),
            }
            for row in transaction_history
        ],
        "spendingHighlights": {
            "highestSingleSpend": {
                "amount": _round(highest["Debit"]) if highest is not None else 0.0,
                "description": str(highest["Description"]) if highest is not None else "-",
                "date": highest["Date"].strftime("%Y-%m-%d") if highest is not None else "-",
            },
            "lowestSingleSpend": {
                "amount": _round(lowest["Debit"]) if lowest is not None else 0.0,
                "description": str(lowest["Description"]) if lowest is not None else "-",
                "date": lowest["Date"].strftime("%Y-%m-%d") if lowest is not None else "-",
            },
        },
    })
