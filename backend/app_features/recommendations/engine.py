def _money(value: float) -> str:
    return f"\u20a6{value:,.0f}"


def build_recommendations(params: dict) -> list[dict]:
    p = params
    anomaly_text = (
        f"Unusual spending was detected in {', '.join(p['anomaly_months'][:3])}."
        if p["has_anomaly"] else "No unusual spending period was detected."
    )

    if p["shap_result"]:
        direction = "increasing" if p["shap_result"]["dominant_dir"] > 0 else "decreasing"
        shap_text = (
            f"The AI driver is {p['shap_result']['dominant_label']}, which is {direction} predicted spend. "
            "Use this signal to plan the next month before the same pattern repeats."
        )
    else:
        shap_text = "Build more transaction history so the AI can explain spending drivers with stronger confidence."

    return [
        {
            "id": "rec_savings_0",
            "number": 1,
            "text": (
                f"{p['first_name']}, your savings rate is {p['savings_rate']}% from income of "
                f"{_money(p['total_in'])} and spending of {_money(p['total_out'])}. Set a fixed transfer "
                "immediately after income lands, then cap flexible spending for the month."
            ),
        },
        {
            "id": "rec_health_1",
            "number": 2,
            "text": (
                f"{p['first_name']}, your financial health score is {p['health_score']}/85, placing you in "
                f"{p['status']}. Focus first on improving savings rate and reducing leakage, because those "
                "are the fastest levers in this score."
            ),
        },
        {
            "id": "rec_leakage_2",
            "number": 3,
            "text": (
                f"{p['first_name']}, financial leakage is {_money(p['leakage_spend'])}, or "
                f"{p['leakage_pct']}% of spending. Review {', '.join(p['leakage_cats'][:5])} "
                "transactions, then remove or reduce anything avoidable."
            ),
        },
        {
            "id": "rec_category_3",
            "number": 4,
            "text": (
                f"{p['first_name']}, {p['top_category']} is your top spending category at "
                f"{_money(p['top_category_amt'])}, equal to {p['top_category_pct']}% of all spending. "
                "Give that category a monthly limit and check it weekly before it runs ahead."
            ),
        },
        {
            "id": "rec_shap_4",
            "number": 5,
            "text": f"{p['first_name']}, {anomaly_text} {shap_text}",
        },
    ]
