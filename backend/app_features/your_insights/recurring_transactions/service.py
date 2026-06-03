import pandas as pd
from utils.data_loader import load_user_dataframe


def get_recurring_transactions(user_name: str) -> dict:
    user_df = load_user_dataframe(user_name)
    user_df = user_df.copy()
    user_df['YearMonth'] = user_df['Date'].dt.to_period('M')
    total_months = user_df['YearMonth'].nunique()

    # Clean description — strip noise to find recurring patterns
    user_df['Desc_Clean'] = user_df['Description'].str.strip().str.lower()
    user_df['Desc_Clean'] = user_df['Desc_Clean'].str.replace(r'\s+', ' ', regex=True)

    # Group by description — count how many distinct months it appears in
    recurrence = user_df[user_df['Debit'] > 0].groupby('Desc_Clean').agg(
        Months_Seen=('YearMonth', 'nunique'),
        Total_Times=('Debit', 'count'),
        Avg_Amount=('Debit', 'mean'),
        Total_Spent=('Debit', 'sum'),
        Category=('Category', 'first')
    ).reset_index()

    # A transaction is "recurring" if it appears in 3+ distinct months
    recurring = recurrence[recurrence['Months_Seen'] >= 3].sort_values(
        'Months_Seen', ascending=False).reset_index(drop=True)

    recurring['Consistency_%'] = (recurring['Months_Seen'] / total_months * 100).round(1)
    recurring['Desc_Display'] = recurring['Desc_Clean'].str.title().str[:40]

    # Estimated monthly committed spend
    monthly_committed = recurring['Avg_Amount'].sum()

    return {
        "rows": [
            {
                "description": row['Desc_Display'],
                "frequencyPct": float(row['Consistency_%']),
                "monthsRepeated": int(row['Months_Seen']),
                "totalMonths": total_months,
                "avgAmount": float(row['Avg_Amount'])
            }
            for _, row in recurring.head(15).iterrows()
        ],
        "patternSummary": f"{len(recurring)} recurring transactions detected across {total_months} months. These appear in 3 or more distinct months, suggesting regular patterns in spending or income.",
    }
