import pandas as pd
from utils.data_loader import load_user_dataframe


def get_spending_behaviour_patterns(user_name: str) -> dict:
    user_df = load_user_dataframe(user_name)
    user_df = user_df.copy()
    user_df['IsWeekend'] = user_df['Date'].dt.dayofweek.isin([5, 6]).astype(int)
    user_df['DayOfWeek'] = user_df['Date'].dt.day_name()
    user_df['YearMonth'] = user_df['Date'].dt.to_period('M')

    # Weekend vs Weekday
    weekend_spend = user_df[user_df['IsWeekend'] == 1]['Debit'].sum()
    weekday_spend = user_df[user_df['IsWeekend'] == 0]['Debit'].sum()
    weekend_txns = len(user_df[user_df['IsWeekend'] == 1])
    weekday_txns = len(user_df[user_df['IsWeekend'] == 0])
    weekend_avg = weekend_spend / weekend_txns if weekend_txns > 0 else 0
    weekday_avg = weekday_spend / weekday_txns if weekday_txns > 0 else 0

    # Monthly spending stats
    monthly_exp = user_df.groupby(user_df['Date'].dt.to_period('M'))['Debit'].sum()
    most_expensive_month = monthly_exp.idxmax()
    cheapest_month = monthly_exp.idxmin()
    avg_monthly = monthly_exp.mean()
    std_monthly = monthly_exp.std()

    # Transaction size distribution
    bins = [0, 500, 2000, 10000, 50000, float('inf')]
    labels = ['Micro (₦0–500)', 'Small (₦501–2K)', 'Medium (₦2K–10K)', 'Large (₦10K–50K)', 'Very Large (₦50K+)']
    debit_only = user_df[user_df['Debit'] > 0].copy()
    debit_only['TxnSize'] = pd.cut(debit_only['Debit'], bins=bins, labels=labels)
    txn_dist = debit_only['TxnSize'].value_counts().sort_index()

    # Category consistency across months
    total_months = user_df['YearMonth'].nunique()
    cat_months = user_df.groupby('Category')['YearMonth'].nunique().sort_values(ascending=False)

    # Spending by day of week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    spending_by_day = user_df.groupby('DayOfWeek')['Debit'].sum().reindex(day_order, fill_value=0)
    spending_by_day_list = [
        {"day": day, "amount": float(amount)}
        for day, amount in spending_by_day.items()
    ]

    return {
        "weekendTotal": float(weekend_spend),
        "weekdayTotal": float(weekday_spend),
        "weekendAvg": float(weekend_avg),
        "weekdayAvg": float(weekday_avg),
        "mostExpensiveMonth": {
            "month": str(most_expensive_month),
            "amount": float(monthly_exp.max())
        },
        "cheapestMonth": {
            "month": str(cheapest_month),
            "amount": float(monthly_exp.min())
        },
        "avgMonthlySpend": float(avg_monthly),
        "stdDeviation": float(std_monthly),
        "sizeDistribution": [
            {
                "bucket": label.split(' (')[0].replace('₦', ''),
                "range": label.split(' (')[1].replace(')', ''),
                "count": int(count),
                "total": float(debit_only[debit_only['TxnSize'] == label]['Debit'].sum())
            }
            for label, count in txn_dist.items()
        ],
        "categoryConsistency": [
            {
                "category": cat,
                "consistencyPct": round((months / total_months * 100), 1)
            }
            for cat, months in cat_months.items()
        ],
        "spendingByDayOfWeek": spending_by_day_list
    }
