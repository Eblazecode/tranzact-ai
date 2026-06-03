import pandas as pd
from utils.data_loader import load_user_dataframe


def get_financial_leakage(user_name: str) -> dict:
    user_df = load_user_dataframe(user_name)
    
    # Define leakage categories
    leakage_cats = ['Betting', 'Charges', 'SMS Charges', 'Card Maintenance', 'Tax']
    leakage = user_df[user_df['Category'].isin(leakage_cats)]
    total_spend = user_df['Debit'].sum()
    leakage_spend = leakage['Debit'].sum()
    leakage_pct = leakage_spend / total_spend * 100 if total_spend > 0 else 0
    
    # Per-category breakdown within leakage
    leakage_by_cat = leakage.groupby('Category')['Debit'].agg(['sum', 'count']).round(2)
    
    # Spend breakdown for pie chart
    productive_cats = ['Savings', 'Data Purchase', 'Airtime', 'Electricity', 'School']
    productive = user_df[user_df['Category'].isin(productive_cats)]['Debit'].sum()
    p2p = user_df[user_df['Category'] == 'P2P Transfer']['Debit'].sum()
    pos = user_df[user_df['Category'] == 'POS Transaction']['Debit'].sum()
    other_sp = max(total_spend - leakage_spend - productive - p2p - pos, 0)
    
    spend_breakdown = {
        'P2P Transfers': float(p2p),
        'POS Purchases': float(pos),
        'Productive': float(productive),
        'Leakage': float(leakage_spend),
        'Other': float(other_sp)
    }
    
    # Filter out zero values
    spend_breakdown = {k: v for k, v in spend_breakdown.items() if v > 0}
    
    return {
        "totalLeakageAmount": float(leakage_spend),
        "leakagePct": float(leakage_pct),
        "leakageTransactionCount": int(len(leakage)),
        "breakdown": [
            {
                "category": cat,
                "amount": float(row['sum']),
                "count": int(row['count']),
                "avg": float(row['sum'] / row['count'])
            }
            for cat, row in leakage_by_cat.iterrows()
        ],
        "bucketBreakdown": [
            {"bucket": bucket, "amount": amount}
            for bucket, amount in spend_breakdown.items()
        ],
        "amountByCategory": [
            {"category": cat, "amount": float(row['sum'])}
            for cat, row in leakage_by_cat.iterrows()
        ]
    }
