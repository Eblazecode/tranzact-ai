import pandas as pd
import numpy as np
from utils.data_loader import load_user_dataframe


def flag_anomalies(series, threshold=2.0):
    mean = series.mean()
    std = series.std()
    z_scores = (series - mean) / std
    anomalies = z_scores.abs() > threshold
    return anomalies, z_scores, mean, std


def get_anomalies(user_name: str) -> dict:
    user_df = load_user_dataframe(user_name)
    user_df = user_df.copy()
    user_df['YearMonth'] = user_df['Date'].dt.to_period('M')
    user_df['YearWeek'] = user_df['Date'].dt.to_period('W')

    # Monthly and weekly spending
    monthly_spend = user_df.groupby('YearMonth')['Debit'].sum().reset_index()
    monthly_spend = monthly_spend.rename(columns={'Debit': 'Total_Spent'})
    
    weekly_spend = user_df.groupby('YearWeek')['Debit'].sum().reset_index()
    weekly_spend = weekly_spend.rename(columns={'Debit': 'Total_Spent'})

    # Detect anomalies
    monthly_spend['Anomaly'], monthly_spend['Z_Score'], m_mean, m_std = flag_anomalies(monthly_spend['Total_Spent'])
    weekly_spend['Anomaly'], weekly_spend['Z_Score'], w_mean, w_std = flag_anomalies(weekly_spend['Total_Spent'])

    # Get flagged months and weeks
    anomalous_months = monthly_spend[monthly_spend['Anomaly']]
    anomalous_weeks = weekly_spend[weekly_spend['Anomaly']]

    return {
        "flaggedMonths": [
            {
                "month": str(row['YearMonth']),
                "zScore": float(row['Z_Score']),
                "amount": float(row['Total_Spent'])
            }
            for _, row in anomalous_months.iterrows()
        ],
        "flaggedWeeks": [
            {
                "week": str(row['YearWeek']),
                "zScore": float(row['Z_Score']),
                "amount": float(row['Total_Spent'])
            }
            for _, row in anomalous_weeks.iterrows()
        ],
        "monthlySeries": [
            {
                "month": str(row['YearMonth']),
                "amount": float(row['Total_Spent']),
                "isAnomaly": bool(row['Anomaly'])
            }
            for _, row in monthly_spend.iterrows()
        ],
        "weeklySeries": [
            {
                "week": str(row['YearWeek']),
                "amount": float(row['Total_Spent']),
                "isAnomaly": bool(row['Anomaly'])
            }
            for _, row in weekly_spend.iterrows()
        ]
    }
