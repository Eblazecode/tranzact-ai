import subprocess
import warnings

import numpy as np
import pandas as pd
from fastapi import HTTPException, status
from sklearn.ensemble import GradientBoostingRegressor

try:
    import shap
except ImportError:
    subprocess.run(["pip", "install", "shap", "-q"])
    import shap

from utils.data_loader import load_user_dataframe

from .schemas import MonthlyPredictionRequest

warnings.filterwarnings("ignore")

FEATURE_COLS = [
    "Month_Index",
    "Month_Num",
    "Total_Received",
    "Avg_Balance",
    "Unique_Categories",
    "Transaction_Count",
    "Spent_Lag1",
    "Spent_Lag2",
    "Received_Lag1",
    "Spent_Rolling3",
    "Spend_Momentum",
]

FEATURE_LABELS = {
    "Month_Index": "Position in data timeline (month no.)",
    "Month_Num": "Calendar month (Jan=1 ... Dec=12)",
    "Total_Received": "Total money received this month (Naira)",
    "Avg_Balance": "Average account balance this month (Naira)",
    "Unique_Categories": "No. of different spending categories used",
    "Transaction_Count": "Total number of transactions made",
    "Spent_Lag1": "Total spent last month (Naira)",
    "Spent_Lag2": "Total spent 2 months ago (Naira)",
    "Received_Lag1": "Total money received last month (Naira)",
    "Spent_Rolling3": "3-month rolling average spend (Naira)",
    "Spend_Momentum": "Month-on-month spending change (Naira, + = rose, - = dropped)",
}


def _size_word_from_push(dominant_push: float) -> str:
    if dominant_push >= 10000:
        return "massively"
    if dominant_push >= 5000:
        return "strongly"
    if dominant_push >= 1000:
        return "moderately"
    if dominant_push >= 500:
        return "slightly"
    return "marginally"


def _clean_label(feat: str) -> str:
    return FEATURE_LABELS[feat].split("(")[0].strip().lower()


def _monthly_plain_english_lines(
    dominant: str,
    dominant_dir: float,
    predict_month_label: str,
    user_name: str,
    future_vals: dict[str, float],
) -> list[str]:
    user_display_name = user_name.split()[0].upper()
    spend_word = "more" if dominant_dir > 0 else "less"

    if dominant == "Spend_Momentum":
        momentum_val = float(future_vals.get("Spend_Momentum", 0))
        if momentum_val < 0:
            if dominant_dir > 0:
                return [
                    "The previous month's spending dropped sharply.",
                    f"The AI learned that when {user_display_name} has a big spending drop,",
                    f"a rebound tends to follow - so it expects {user_display_name} to spend {spend_word} in {predict_month_label}.",
                ]
            return [
                "The previous month's spending dropped sharply.",
                "The AI learned that this kind of drop tends to continue,",
                f"so it expects {user_display_name} to spend {spend_word} in {predict_month_label}.",
            ]

        if momentum_val > 0:
            if dominant_dir > 0:
                return [
                    "The previous month's spending rose sharply.",
                    "The AI learned that this kind of rise tends to carry forward,",
                    f"so it expects {user_display_name} to spend {spend_word} in {predict_month_label}.",
                ]
            return [
                "The previous month's spending rose sharply.",
                f"The AI learned that when {user_display_name} has a big spending rise,",
                f"a pullback tends to follow - so it expects {user_display_name} to spend {spend_word} in {predict_month_label}.",
            ]

        return [
            "There was no change in spending between the last two months.",
            f"The AI expects {user_display_name} to spend a similar amount in {predict_month_label}.",
        ]

    direction_word = "HIGH" if dominant_dir > 0 else "LOW"
    return [
        f"The AI sees {_clean_label(dominant)} is {direction_word}",
        f"compared to past months, so it expects {user_display_name} to spend {spend_word} in {predict_month_label}.",
    ]


def get_monthly_prediction(payload: MonthlyPredictionRequest) -> dict:
    user_df = load_user_dataframe(payload.user_name).copy()
    user_df["Date"] = pd.to_datetime(user_df["Date"])

    monthly = (
        user_df
        .set_index("Date")
        .resample("ME")
        .agg({
            "Debit": "sum",
            "Credit": "sum",
            "Balance": "mean",
            "Category": "nunique",
            "Description": "count",
        })
        .fillna(0)
        .reset_index()
    )

    monthly.rename(columns={
        "Debit": "Total_Spent",
        "Credit": "Total_Received",
        "Balance": "Avg_Balance",
        "Category": "Unique_Categories",
        "Description": "Transaction_Count",
    }, inplace=True)

    monthly["Month_Label"] = monthly["Date"].dt.strftime("%b %Y")
    monthly["Month_Index"] = np.arange(len(monthly))
    monthly["Month_Num"] = monthly["Date"].dt.month
    monthly["Spent_Lag1"] = monthly["Total_Spent"].shift(1).fillna(0)
    monthly["Spent_Lag2"] = monthly["Total_Spent"].shift(2).fillna(0)
    monthly["Received_Lag1"] = monthly["Total_Received"].shift(1).fillna(0)
    monthly["Spent_Rolling3"] = monthly["Total_Spent"].rolling(3, min_periods=1).mean()
    monthly["Spend_Momentum"] = monthly["Total_Spent"].diff().fillna(0)

    if len(monthly) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"User '{payload.user_name}' has less than 2 months of data - cannot build lag features.",
        )

    predict_date = pd.Timestamp(year=payload.predict_year, month=payload.predict_month_num, day=1)
    predict_month_label = predict_date.strftime("%b %Y")
    monthly_train = monthly[monthly["Date"] < predict_date].copy()
    actual_row = monthly[monthly["Date"].dt.to_period("M") == predict_date.to_period("M")]
    actual_spend = actual_row["Total_Spent"].values[0] if len(actual_row) > 0 else None

    if len(monthly_train) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Not enough months before target month to train.",
        )

    X_train = monthly_train[FEATURE_COLS].values
    y_train = monthly_train["Total_Spent"].values

    last = monthly_train.iloc[-1]
    second_last = monthly_train.iloc[-2]
    future_rolling3 = monthly_train["Total_Spent"].tail(3).mean()
    future_momentum = last["Total_Spent"] - second_last["Total_Spent"]

    same_month_last_year = monthly_train[monthly_train["Month_Num"] == payload.predict_month_num]
    est_received = same_month_last_year["Total_Received"].values[-1] if len(same_month_last_year) > 0 else monthly_train["Total_Received"].mean()
    est_balance = same_month_last_year["Avg_Balance"].values[-1] if len(same_month_last_year) > 0 else monthly_train["Avg_Balance"].mean()
    est_cats = same_month_last_year["Unique_Categories"].values[-1] if len(same_month_last_year) > 0 else monthly_train["Unique_Categories"].mean()
    est_txns = same_month_last_year["Transaction_Count"].values[-1] if len(same_month_last_year) > 0 else monthly_train["Transaction_Count"].mean()

    X_future = np.array([[
        len(monthly_train),
        payload.predict_month_num,
        est_received,
        est_balance,
        est_cats,
        est_txns,
        last["Total_Spent"],
        second_last["Total_Spent"],
        last["Total_Received"],
        future_rolling3,
        future_momentum,
    ]])
    future_vals = dict(zip(FEATURE_COLS, X_future[0]))

    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
    )
    model.fit(X_train, y_train)
    y_pred = max(float(model.predict(X_future)[0]), 0.0)

    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(X_future)[0]
    shap_all = explainer.shap_values(X_train)
    base_value = float(np.array(explainer.expected_value).flatten()[0])
    shap_series = pd.Series(shap_vals, index=FEATURE_COLS)

    top_up = shap_series[shap_series > 0].nlargest(3)
    top_down = shap_series[shap_series < 0].nsmallest(3)
    dominant = shap_series.abs().idxmax()
    dominant_dir = float(shap_series[dominant])
    dominant_push = abs(dominant_dir)
    total_up = float(shap_series[shap_series > 0].sum())
    total_down = float(shap_series[shap_series < 0].abs().sum())

    if dominant_dir > 0:
        dominant_pct = min((dominant_push / total_up * 100), 100) if total_up > 0 else 0
        pressure_label = "upward"
    else:
        dominant_pct = min((dominant_push / total_down * 100), 100) if total_down > 0 else 0
        pressure_label = "downward"

    shap_waterfall = [
        {
            "label": FEATURE_LABELS.get(feature, feature),
            "value": float(value),
            "direction": "up" if value > 0 else "down",
        }
        for feature, value in shap_series.reindex(shap_series.abs().sort_values().index).items()
    ]

    spending_dna = [
        {
            "label": FEATURE_LABELS.get(feature, feature),
            "importance": float(np.abs(shap_all[:, idx]).mean()),
        }
        for idx, feature in enumerate(FEATURE_COLS)
    ]
    spending_dna.sort(key=lambda item: item["importance"])

    return {
        "predictMonthLabel": predict_month_label,
        "startingBaseline": base_value,
        "aiForecast": y_pred,
        "actualSpend": float(actual_spend) if actual_spend is not None else None,
        "forecastError": abs(y_pred - float(actual_spend)) if actual_spend is not None else 0,
        "lastKnownMonth": monthly_train["Month_Label"].iloc[-1],
        "forecastAmount": y_pred,
        "baselineAmount": base_value,
        "topUpFactors": [
            {"label": FEATURE_LABELS.get(feature, feature), "value": float(value)}
            for feature, value in top_up.items()
        ],
        "topDownFactors": [
            {"label": FEATURE_LABELS.get(feature, feature), "value": float(value)}
            for feature, value in top_down.items()
        ],
        "bottomLine": {
            "driverLabel": FEATURE_LABELS.get(dominant, dominant),
            "sizeWord": _size_word_from_push(dominant_push),
            "impactAmount": float(dominant_push),
            "impactDirection": "up" if dominant_dir > 0 else "down",
            "pressurePct": float(round(dominant_pct, 1)),
            "pressureLabel": pressure_label,
            "plainEnglishLines": _monthly_plain_english_lines(
                dominant,
                dominant_dir,
                predict_month_label,
                payload.user_name,
                future_vals,
            ),
        },
        "shapWaterfall": shap_waterfall,
        "spendingDna": spending_dna,
    }
