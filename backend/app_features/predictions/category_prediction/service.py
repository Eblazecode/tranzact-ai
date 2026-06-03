import subprocess

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

try:
    import shap
except ImportError:
    subprocess.run(["pip", "install", "shap", "-q"])
    import shap

from utils.data_loader import load_user_dataframe

from .schemas import CategoryPredictionRequest

CAT_FEATURE_LABELS = {
    "Month_Index": "Position in timeline (training month #)",
    "Month_Num": "Calendar month (Jan=1 ... Dec=12)",
    "Spent_Lag1": "Spend in this category last month (Naira)",
    "Spent_Lag2": "Spend in this category 2 months ago (Naira)",
    "Spent_Rolling3": "3-month rolling average for this category (Naira)",
    "Spend_Momentum": "Month-on-month change in this category (Naira, + = rose, - = dropped)",
}

CAT_FEATURE_COLS = [
    "Month_Index",
    "Month_Num",
    "Spent_Lag1",
    "Spent_Lag2",
    "Spent_Rolling3",
    "Spend_Momentum",
]


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


def _category_plain_english_lines(
    dominant: str,
    dominant_dir: float,
    category_name: str,
    user_name: str,
    predict_month_label: str,
    future_vals: dict[str, float],
    train_df: pd.DataFrame,
) -> list[str]:
    user_display_name = user_name.split()[0].upper()
    spend_word = "MORE" if dominant_dir > 0 else "LESS"

    if dominant == "Spend_Momentum":
        momentum_val = float(future_vals.get("Spend_Momentum", 0))
        if momentum_val < 0:
            if dominant_dir > 0:
                return [
                    f"Last month's [{category_name}] spending dropped by N{abs(momentum_val):,.0f}.",
                    f"The AI learned that after a drop in [{category_name}] spending,",
                    f"a rebound tends to follow - so it predicts {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
                ]
            return [
                f"Last month's [{category_name}] spending dropped by N{abs(momentum_val):,.0f}.",
                f"The AI learned that this kind of drop in [{category_name}] spending",
                f"tends to continue - so it predicts {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
            ]
        if momentum_val > 0:
            if dominant_dir > 0:
                return [
                    f"Last month's [{category_name}] spending rose by N{abs(momentum_val):,.0f}.",
                    f"The AI learned that this kind of rise in [{category_name}] spending",
                    f"tends to carry forward - so it predicts {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
                ]
            return [
                f"Last month's [{category_name}] spending rose by N{abs(momentum_val):,.0f}.",
                f"The AI learned that after a rise in [{category_name}] spending,",
                f"a pullback tends to follow - so it predicts {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
            ]

    if dominant == "Month_Num":
        month_history = train_df[train_df["Month_Num"] == int(future_vals["Month_Num"])]["Debit"]
        overall_mean = float(train_df["Debit"].mean())
        season_word = "HIGH" if dominant_dir > 0 else "LOW"
        if len(month_history) <= 1:
            return [
                f"The AI has identified {predict_month_label.split()[0]} as a seasonally {season_word} spending month for [{category_name}]",
                "based on the pattern of spending across all months in the training data.",
                f"It predicts {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
            ]
        month_mean = float(month_history.mean())
        return [
            f"Historically, {predict_month_label.split()[0]} tends to be a {season_word} spending month for [{category_name}]",
            f"(avg N{month_mean:,.0f} in that month vs overall avg N{overall_mean:,.0f}).",
            f"The AI is using this seasonal pattern to predict {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
        ]

    if dominant == "Spent_Rolling3":
        rolling_val = float(future_vals["Spent_Rolling3"])
        overall_mean = float(train_df["Debit"].mean())
        level_word = "ABOVE" if rolling_val > overall_mean else "BELOW"
        trend_phrase = "elevated" if rolling_val > overall_mean else "low"
        return [
            f"The 3-month rolling average for [{category_name}] is N{rolling_val:,.0f},",
            f"which is {level_word} the overall average of N{overall_mean:,.0f}.",
            f"The AI sees recent spending as {trend_phrase} and predicts {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
        ]

    if dominant == "Spent_Lag1":
        lag1_val = float(future_vals["Spent_Lag1"])
        overall_mean = float(train_df["Debit"].mean())
        level_word = "HIGH" if lag1_val > overall_mean else "LOW"
        diverging = (level_word == "LOW" and dominant_dir > 0) or (level_word == "HIGH" and dominant_dir < 0)
        if diverging:
            return [
                f"Last month's [{category_name}] spend was N{lag1_val:,.0f}, which is {level_word}",
                f"compared to the usual average of N{overall_mean:,.0f}.",
                f"Despite this, other patterns in the data led the AI to predict {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
            ]
        return [
            f"Last month's [{category_name}] spend was N{lag1_val:,.0f}, which is {level_word}",
            f"compared to the usual average of N{overall_mean:,.0f}.",
            f"The AI is carrying this forward and predicts {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
        ]

    if dominant == "Spent_Lag2":
        lag2_val = float(future_vals["Spent_Lag2"])
        overall_mean = float(train_df["Debit"].mean())
        level_word = "HIGH" if lag2_val > overall_mean else "LOW"
        diverging = (level_word == "LOW" and dominant_dir > 0) or (level_word == "HIGH" and dominant_dir < 0)
        if lag2_val == 0:
            direction_label = "UP" if dominant_dir > 0 else "DOWN"
            return [
                f"[{category_name}] spending two months ago was N0 (no recorded spend in that month).",
                f"The AI still pushed the forecast {direction_label} - this is a SHAP quirk:",
                "the absence of spend two months ago is itself a pattern the model learned from.",
                f"Net result: the AI predicts {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
            ]
        if diverging:
            return [
                f"[{category_name}] spending two months ago was N{lag2_val:,.0f}, which is {level_word}",
                f"compared to the usual average of N{overall_mean:,.0f}.",
                f"Despite this, other patterns in the data led the AI to predict {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
            ]
        return [
            f"[{category_name}] spending two months ago was N{lag2_val:,.0f}, which is {level_word}",
            f"compared to the usual average of N{overall_mean:,.0f}.",
            f"The AI is factoring this in and predicts {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
        ]

    if dominant == "Month_Index":
        trend_word = "UPWARD" if dominant_dir > 0 else "DOWNWARD"
        verb = "growth" if dominant_dir > 0 else "decline"
        return [
            f"Over time, {user_display_name}'s [{category_name}] spending has been trending {trend_word}.",
            f"The AI is following this {verb} trend and predicts {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
        ]

    return [
        f"The AI sees {CAT_FEATURE_LABELS[dominant].split('(')[0].strip().lower()} for [{category_name}] is",
        f"{'higher' if dominant_dir > 0 else 'lower'} than usual, so it predicts {user_display_name} will spend {spend_word} on [{category_name}] in {predict_month_label}.",
    ]


def get_category_prediction(payload: CategoryPredictionRequest) -> dict:
    user_df = load_user_dataframe(payload.user_name).copy()
    user_df["Date"] = pd.to_datetime(user_df["Date"])
    user_df["Debit"] = pd.to_numeric(user_df["Debit"], errors="coerce").fillna(0)

    monthly_cat = (
        user_df
        .set_index("Date")
        .groupby("Category")
        .resample("ME")["Debit"]
        .sum()
        .reset_index()
    )

    predict_date = pd.Timestamp(year=payload.predict_year, month=payload.predict_month_num, day=1)
    predict_month_label = predict_date.strftime("%b %Y")
    categories = monthly_cat["Category"].unique()
    all_results = []

    for category_name in sorted(categories):
        cat_df = (
            monthly_cat[monthly_cat["Category"] == category_name]
            .sort_values("Date")
            .reset_index(drop=True)
        )

        train_df = cat_df[cat_df["Date"] < predict_date].copy()
        actual_row = cat_df[cat_df["Date"].dt.to_period("M") == predict_date.to_period("M")]
        actual_spend = actual_row["Debit"].values[0] if len(actual_row) > 0 else None

        if len(train_df) < 3:
            continue

        train_df = train_df.reset_index(drop=True)
        train_df["Month_Index"] = np.arange(len(train_df))
        train_df["Month_Num"] = train_df["Date"].dt.month
        train_df["Spent_Lag1"] = train_df["Debit"].shift(1).fillna(0)
        train_df["Spent_Lag2"] = train_df["Debit"].shift(2).fillna(0)
        train_df["Spent_Rolling3"] = train_df["Debit"].rolling(3, min_periods=1).mean()
        train_df["Spend_Momentum"] = train_df["Debit"].diff().fillna(0)

        X_train = train_df[CAT_FEATURE_COLS].values
        y_train = train_df["Debit"].values

        last = train_df.iloc[-1]
        second_last = train_df.iloc[-2]
        future_rolling3 = train_df["Debit"].tail(3).mean()
        future_momentum = last["Debit"] - second_last["Debit"]

        X_future = np.array([[
            len(train_df),
            payload.predict_month_num,
            last["Debit"],
            second_last["Debit"],
            future_rolling3,
            future_momentum,
        ]])
        future_vals = dict(zip(CAT_FEATURE_COLS, X_future[0]))

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
        base_value = float(np.array(explainer.expected_value).flatten()[0])
        shap_series = pd.Series(shap_vals, index=CAT_FEATURE_COLS)

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

        all_results.append({
            "predictMonthLabel": predict_month_label,
            "categoryName": category_name,
            "predictedSpend": y_pred,
            "startingBaseline": base_value,
            "aiForecast": y_pred,
            "actualSpend": float(actual_spend) if actual_spend is not None else None,
            "forecastError": abs(y_pred - float(actual_spend)) if actual_spend is not None else 0,
            "lastKnownMonth": train_df["Date"].iloc[-1].strftime("%b %Y"),
            "topUpFactors": [
                {"label": CAT_FEATURE_LABELS.get(feature, feature), "value": float(value)}
                for feature, value in top_up.items()
            ],
            "topDownFactors": [
                {"label": CAT_FEATURE_LABELS.get(feature, feature), "value": float(value)}
                for feature, value in top_down.items()
            ],
            "bottomLine": {
                "driverLabel": CAT_FEATURE_LABELS.get(dominant, dominant),
                "sizeWord": _size_word_from_push(dominant_push),
                "impactAmount": float(dominant_push),
                "impactDirection": "up" if dominant_dir > 0 else "down",
                "pressurePct": float(round(dominant_pct, 1)),
                "pressureLabel": pressure_label,
                "plainEnglishLines": _category_plain_english_lines(
                    dominant,
                    dominant_dir,
                    category_name,
                    payload.user_name,
                    predict_month_label,
                    future_vals,
                    train_df,
                ),
            },
            "shapWaterfall": [
                {
                    "label": CAT_FEATURE_LABELS.get(feature, feature),
                    "value": float(value),
                    "direction": "up" if value > 0 else "down",
                }
                for feature, value in shap_series.reindex(shap_series.abs().sort_values().index).items()
            ],
        })

    return all_results
