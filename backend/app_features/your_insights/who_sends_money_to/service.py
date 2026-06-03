import pandas as pd
from utils.data_loader import load_user_dataframe


def get_transfers_out(user_name: str, filter_by: str, period: str, top_n: int) -> dict:
    user_df = load_user_dataframe(user_name)
    user_df = user_df.copy()
    user_df['YearMonth'] = user_df['Date'].dt.to_period('M')
    user_df['YearWeek'] = user_df['Date'].dt.to_period('W')
    user_df['Year'] = user_df['Date'].dt.year

    # Keep only outgoing P2P transfers
    sent = user_df[
        (user_df['Category'] == 'P2P Transfer') &
        (user_df['Description'].str.lower().str.startswith('transfer to', na=False))
    ].copy()

    # Extract recipient name
    sent['Recipient'] = sent['Description'].str.replace(
        r'^Transfer to\s+', '', case=False, regex=True).str.strip()

    # Filter by period
    if filter_by == 'month':
        available = sorted([str(p) for p in user_df['YearMonth'].unique()])
        if period == 'all' or period not in available:
            subset = sent
        else:
            subset = sent[sent['YearMonth'].astype(str) == period]
    elif filter_by == 'week':
        available = sorted([str(p) for p in user_df['YearWeek'].unique()])
        if period == 'all' or period not in available:
            subset = sent
        else:
            subset = sent[sent['YearWeek'].astype(str) == period]
    elif filter_by == 'year':
        available = sorted([str(p) for p in user_df['Year'].unique()])
        if period == 'all' or period not in available:
            subset = sent
        else:
            subset = sent[sent['Year'] == int(period)]
    else:
        available = []
        subset = sent

    # Get top N recipients
    recipient_count = subset.groupby('Recipient')['Debit'].count().sort_values(ascending=False).head(top_n)
    recipient_amount = subset.groupby('Recipient')['Debit'].sum().reindex(recipient_count.index)

    return {
        "availableMonths": sorted([str(p) for p in user_df['YearMonth'].unique()]),
        "availableWeeks": sorted([str(p) for p in user_df['YearWeek'].unique()]),
        "availableYears": sorted([str(p) for p in user_df['Year'].unique()]),
        "table": [
            {
                "name": recipient,
                "frequency": int(recipient_count[recipient]),
                "totalSent": float(recipient_amount[recipient])
            }
            for recipient in recipient_count.index
        ],
        "transferCountByRecipient": [
            {"name": recipient, "count": int(recipient_count[recipient])}
            for recipient in recipient_count.index
        ],
        "amountSentByRecipient": [
            {"name": recipient, "amount": float(recipient_amount[recipient])}
            for recipient in recipient_count.index
        ]
    }
