import pandas as pd
from utils.data_loader import load_user_dataframe


def get_balance_trajectory(user_name: str) -> dict:
    user_df = load_user_dataframe(user_name)
    user_df = user_df.copy()
    user_df = user_df.sort_values('Date').reset_index(drop=True)
    user_df['YearMonth'] = user_df['Date'].dt.to_period('M')

    # Daily closing balance (last balance entry per day)
    daily_balance = user_df.groupby('Date')['Balance'].last().reset_index()
    daily_balance['Rolling30'] = daily_balance['Balance'].rolling(30).mean()

    # Monthly average balance
    monthly_balance = user_df.groupby('YearMonth')['Balance'].mean().reset_index()
    monthly_balance['Month_str'] = monthly_balance['YearMonth'].astype(str)
    monthly_balance['MoM_Change'] = monthly_balance['Balance'].diff()

    # Key stats
    starting_balance = float(daily_balance['Balance'].iloc[0])
    ending_balance = float(daily_balance['Balance'].iloc[-1])
    peak_balance = float(daily_balance['Balance'].max())
    peak_date = daily_balance.loc[daily_balance['Balance'].idxmax(), 'Date'].strftime('%Y-%m-%d')
    lowest_balance = float(daily_balance['Balance'].min())
    lowest_date = daily_balance.loc[daily_balance['Balance'].idxmin(), 'Date'].strftime('%Y-%m-%d')
    avg_balance = float(daily_balance['Balance'].mean())
    danger_days = int((daily_balance['Balance'] < 1000).sum())

    return {
        "startingBalance": starting_balance,
        "endingBalance": ending_balance,
        "peakBalance": {
            "amount": peak_balance,
            "date": peak_date
        },
        "lowestBalance": {
            "amount": lowest_balance,
            "date": lowest_date
        },
        "avgBalance": avg_balance,
        "dangerZoneDays": danger_days,
        "dailyClosing": [
            {
                "date": row['Date'].strftime('%Y-%m-%d'),
                "balance": float(row['Balance'])
            }
            for _, row in daily_balance.iterrows()
        ],
        "rolling30Day": [
            {
                "date": row['Date'].strftime('%Y-%m-%d'),
                "balance": float(row['Rolling30'])
            }
            for _, row in daily_balance.iterrows()
        ],
        "monthlyAverage": [
            {
                "month": row['Month_str'],
                "avgBalance": float(row['Balance'])
            }
            for _, row in monthly_balance.iterrows()
        ],
        "monthOverMonthChange": [
            {
                "month": row['Month_str'],
                "change": float(row['MoM_Change']) if pd.notna(row['MoM_Change']) else 0.0
            }
            for _, row in monthly_balance.iterrows()
        ]
    }
