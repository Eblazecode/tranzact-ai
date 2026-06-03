import pandas as pd


def _flag_anomalies(series, threshold=2.0):
    std = series.std()
    if pd.isna(std) or std == 0:
        return pd.Series(False, index=series.index)
    z_score = (series - series.mean()) / std
    return z_score.abs() > threshold


def compute_health_score(
    savings_rate: float,
    user_df: pd.DataFrame,
) -> dict:
    """3-factor health score out of 85 used across the application.

    Factors:
        Savings  (max 40) — based on savings rate percentage
        Leakage  (max 30) — based on leakage spend and percentage
        Anomaly  (max 15) — based on spending anomaly detection

    Returns dict with: health_score, health_status, savings_score,
    leakage_score, leakage_cats, leakage_spend, leakage_pct,
    anomaly_score, has_anomaly, anomaly_months
    """
    # --- Factor 1: Savings score (max 40) ---
    if savings_rate >= 20:
        savings_score = 40
    elif savings_rate >= 10:
        savings_score = 30
    elif savings_rate >= 0:
        savings_score = 15
    else:
        savings_score = 0

    # --- Factor 2: Leakage score (max 30) ---
    total_out = float(user_df["Debit"].sum())
    all_categories = user_df["Category"].dropna().unique()
    leakage_keywords = ["bet", "charge", "fee", "tax", "fine", "penalty",
                        "maintenance", "sms", "stamp", "levy", "interest"]
    leakage_cats = [
        cat for cat in all_categories
        if any(kw in str(cat).lower() for kw in leakage_keywords)
    ]
    leakage_spend = float(user_df[user_df["Category"].isin(leakage_cats)]["Debit"].sum())
    leakage_pct = (leakage_spend / total_out * 100) if total_out > 0 else 0

    if leakage_pct <= 5 and leakage_spend <= 20000:
        leakage_score = 30
    elif leakage_pct <= 15 or leakage_spend <= 50000:
        leakage_score = 15
    else:
        leakage_score = 0

    # --- Factor 3: Anomaly score (max 15) ---
    df = user_df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df["YearMonth"] = df["Date"].dt.to_period("M")
    df["YearWeek"] = df["Date"].dt.to_period("W")

    monthly_spend = df.groupby("YearMonth")["Debit"].sum().reset_index()
    monthly_spend.columns = ["YearMonth", "Total_Spent"]
    weekly_spend = df.groupby("YearWeek")["Debit"].sum().reset_index()
    weekly_spend.columns = ["YearWeek", "Total_Spent"]

    monthly_spend["Anomaly"] = _flag_anomalies(monthly_spend["Total_Spent"])
    weekly_spend["Anomaly"] = _flag_anomalies(weekly_spend["Total_Spent"])

    has_anomaly = bool(monthly_spend["Anomaly"].any() or weekly_spend["Anomaly"].any())
    anomaly_months = monthly_spend[monthly_spend["Anomaly"]]["YearMonth"].astype(str).tolist()
    anomaly_score = 15 if not has_anomaly else 5

    # --- Total ---
    health_score = savings_score + leakage_score + anomaly_score
    if health_score >= 70:
        health_status = "EXCELLENT"
    elif health_score >= 50:
        health_status = "MODERATE"
    elif health_score >= 30:
        health_status = "AT RISK"
    else:
        health_status = "CRITICAL"

    return {
        "health_score": health_score,
        "health_status": health_status,
        "savings_score": savings_score,
        "leakage_score": leakage_score,
        "leakage_cats": leakage_cats,
        "leakage_spend": round(leakage_spend, 2),
        "leakage_pct": round(leakage_pct, 1),
        "anomaly_score": anomaly_score,
        "has_anomaly": has_anomaly,
        "anomaly_months": anomaly_months,
    }
