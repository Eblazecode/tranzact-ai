from utils.data_loader import load_user_dataframe
from utils.health_score import compute_health_score


def get_financial_health_summary(user_name: str) -> dict[str, float | str]:
    user_df = load_user_dataframe(user_name)

    total_in = float(user_df["Credit"].sum())
    total_out = float(user_df["Debit"].sum())
    net = total_in - total_out
    savings_rate = ((total_in - total_out) / total_in * 100) if total_in > 0 else 0

    h = compute_health_score(savings_rate, user_df)

    return {
        "totalIncome": round(total_in, 2),
        "totalExpenses": round(total_out, 2),
        "netSavings": round(net, 2),
        "savingsRatePct": round(savings_rate, 2),
        "healthStatus": h["health_status"],
        "healthNarrative": (
            f"Your {'income exceeds expenses' if savings_rate >= 0 else 'expenses exceed income'} with a savings rate of {savings_rate:.1f}%. "
            f"This indicates {'strong financial health' if h['health_score'] >= 70 else 'moderate financial health' if h['health_score'] >= 50 else 'limited financial buffer' if h['health_score'] >= 30 else 'a financial deficit requiring immediate attention'}."
        ),
        "healthScore": h["health_score"],
    }
