import numpy as np
import pandas as pd
import shap
from fastapi import HTTPException, status
from sklearn.ensemble import GradientBoostingRegressor

from utils.data_loader import load_user_dataframe

from .schemas import RecommendationRequest
from .engine import build_recommendations


def get_shap_factors(user_df):
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

    monthly["Month_Index"] = np.arange(len(monthly))
    monthly["Month_Num"] = monthly["Date"].dt.month
    monthly["Spent_Lag1"] = monthly["Total_Spent"].shift(1).fillna(0)
    monthly["Spent_Lag2"] = monthly["Total_Spent"].shift(2).fillna(0)
    monthly["Received_Lag1"] = monthly["Total_Received"].shift(1).fillna(0)
    monthly["Spent_Rolling3"] = monthly["Total_Spent"].rolling(3, min_periods=1).mean()
    monthly["Spend_Momentum"] = monthly["Total_Spent"].diff().fillna(0)

    feature_cols = [
        "Month_Index", "Month_Num", "Total_Received", "Avg_Balance",
        "Unique_Categories", "Transaction_Count", "Spent_Lag1",
        "Spent_Lag2", "Received_Lag1", "Spent_Rolling3", "Spend_Momentum",
    ]

    feature_labels = {
        "Month_Index": "Overall time trend",
        "Month_Num": "Seasonal month pattern",
        "Total_Received": "Income received this month",
        "Avg_Balance": "Average account balance",
        "Unique_Categories": "Diversity of spending categories",
        "Transaction_Count": "Number of transactions",
        "Spent_Lag1": "Last month spending behaviour",
        "Spent_Lag2": "Two months ago spending behaviour",
        "Received_Lag1": "Last month income",
        "Spent_Rolling3": "3-month average spending trend",
        "Spend_Momentum": "Month-on-month spending acceleration",
    }

    if len(monthly) < 3:
        return None

    x_train = monthly[feature_cols].values
    y_train = monthly["Total_Spent"].values

    gb = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
    )
    gb.fit(x_train, y_train)

    explainer = shap.TreeExplainer(gb)
    shap_vals = explainer.shap_values(x_train)
    shap_series = pd.Series(shap_vals[-1], index=feature_cols)

    dominant = shap_series.abs().idxmax()
    top_up = shap_series[shap_series > 0].nlargest(3)
    top_down = shap_series[shap_series < 0].nsmallest(3)

    return {
        "dominant_label": feature_labels[dominant],
        "dominant_dir": shap_series[dominant],
        "up_labels": [feature_labels[f] for f in top_up.index],
        "down_labels": [feature_labels[f] for f in top_down.index],
    }


def _flag_anomalies(series, threshold=2.0):
    std = series.std()
    if pd.isna(std) or std == 0:
        return pd.Series(False, index=series.index)
    z_score = (series - series.mean()) / std
    return z_score.abs() > threshold


def _statement_user_name(user_name: str, user_df: pd.DataFrame) -> str:
    if "User" not in user_df.columns:
        return user_name

    names = user_df["User"].dropna().astype(str).str.strip()
    names = names[(names != "") & (names.str.lower() != "unknown user")]
    if names.empty:
        return user_name

    return names.iloc[0]


def collect_parameters(user_name, user_df):
    user_df = user_df.copy()
    user_df["Date"] = pd.to_datetime(user_df["Date"])
    user_df["YearMonth"] = user_df["Date"].dt.to_period("M")
    user_df["YearWeek"] = user_df["Date"].dt.to_period("W")

    total_in = user_df["Credit"].sum()
    total_out = user_df["Debit"].sum()

    savings_rate = ((total_in - total_out) / total_in * 100) if total_in > 0 else 0

    if savings_rate >= 20:
        savings_score = 40
    elif savings_rate >= 10:
        savings_score = 30
    elif savings_rate >= 0:
        savings_score = 15
    else:
        savings_score = 0

    # Dynamic leakage category detection using keyword matching
    all_categories = user_df["Category"].dropna().unique()
    leakage_keywords = ["bet", "charge", "fee", "tax", "fine", "penalty",
                        "maintenance", "sms", "stamp", "levy", "interest"]
    leakage_cats = [
        cat for cat in all_categories
        if any(kw in str(cat).lower() for kw in leakage_keywords)
    ]
    leakage_spend = user_df[user_df["Category"].isin(leakage_cats)]["Debit"].sum()
    leakage_pct = (leakage_spend / total_out * 100) if total_out > 0 else 0

    if leakage_pct <= 5 and leakage_spend <= 20000:
        leakage_score = 30
    elif leakage_pct <= 15 or leakage_spend <= 50000:
        leakage_score = 15
    else:
        leakage_score = 0

    cat_totals = user_df.groupby("Category")["Debit"].sum()
    if cat_totals.empty:
        top_category = "No spending category"
        top_category_amt = 0
        top_category_pct = 0
    else:
        top_category = cat_totals.idxmax()
        top_category_amt = cat_totals.max()
        top_category_pct = (top_category_amt / total_out * 100) if total_out > 0 else 0

    monthly_spend = user_df.groupby("YearMonth")["Debit"].sum().reset_index()
    monthly_spend.columns = ["YearMonth", "Total_Spent"]
    weekly_spend = user_df.groupby("YearWeek")["Debit"].sum().reset_index()
    weekly_spend.columns = ["YearWeek", "Total_Spent"]

    monthly_spend["Anomaly"] = _flag_anomalies(monthly_spend["Total_Spent"])
    weekly_spend["Anomaly"] = _flag_anomalies(weekly_spend["Total_Spent"])

    has_anomaly = monthly_spend["Anomaly"].any() or weekly_spend["Anomaly"].any()
    anomaly_months = monthly_spend[monthly_spend["Anomaly"]]["YearMonth"].astype(str).tolist()
    anomaly_score = 15 if not has_anomaly else 5

    health_score = savings_score + leakage_score + anomaly_score
    if health_score >= 70:
        health_status = "EXCELLENT"
    elif health_score >= 50:
        health_status = "MODERATE"
    elif health_score >= 30:
        health_status = "AT RISK"
    else:
        health_status = "CRITICAL"

    statement_name = _statement_user_name(user_name, user_df)

    return {
        "user_name": user_name,
        "statement_name": statement_name,
        "first_name": statement_name.split()[0],
        "total_in": round(total_in, 2),
        "total_out": round(total_out, 2),
        "savings_rate": round(savings_rate, 1),
        "health_score": health_score,
        "status": health_status,
        "leakage_cats": leakage_cats,
        "leakage_spend": round(leakage_spend, 2),
        "leakage_pct": round(leakage_pct, 1),
        "top_category": top_category,
        "top_category_amt": round(top_category_amt, 2),
        "top_category_pct": round(top_category_pct, 1),
        "has_anomaly": bool(has_anomaly),
        "anomaly_months": anomaly_months,
        "shap_result": get_shap_factors(user_df),
    }


def get_recommendations(payload: RecommendationRequest) -> dict:
    user_df = load_user_dataframe(payload.user_name)
    params = collect_parameters(payload.user_name, user_df)

    if not params:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for user '{payload.user_name}'.",
        )

    recommendations = build_recommendations(params)

    status_map = {
        "EXCELLENT": "HEALTHY",
        "MODERATE": "MODERATE",
        "AT RISK": "AT RISK",
        "CRITICAL": "CRITICAL",
    }

    return {
        "user": params["statement_name"],
        "healthScore": params["health_score"],
        "healthScoreMax": 85,
        "riskStatus": status_map.get(params["status"], "MODERATE"),
        "totalIncome": params["total_in"],
        "totalSpending": params["total_out"],
        "savingsRatePct": params["savings_rate"],
        "leakageAmount": params["leakage_spend"],
        "leakagePct": params["leakage_pct"],
        "topCategoryName": params["top_category"],
        "topCategoryAmount": params["top_category_amt"],
        "topCategoryPct": params["top_category_pct"],
        "anomalyStatus": "Detected" if params["has_anomaly"] else "None detected",
        "cards": recommendations[:5],
    }



