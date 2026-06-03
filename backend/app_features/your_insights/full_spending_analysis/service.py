import pandas as pd
import numpy as np
from utils.data_loader import load_user_dataframe


def get_spending_analysis(user_name: str) -> dict:
    """
    Comprehensive spending analysis for frontend visualization.
    
    Returns data for:
    - SpendingPieChart (spendByCategory)
    - SpendingHighlights (top10LargestTransactions)
    - SpendingBehaviourPage (behaviour patterns)
    """
    user_df = load_user_dataframe(user_name)
    user_df = user_df.copy()
    
    # Convert date column if not already datetime
    user_df['Date'] = pd.to_datetime(user_df['Date'])
    
    # Add helper columns
    user_df['IsWeekend'] = user_df['Date'].dt.dayofweek.isin([5, 6]).astype(int)
    user_df['DayOfWeek'] = user_df['Date'].dt.day_name()
    user_df['YearMonth'] = user_df['Date'].dt.to_period('M')
    
    # ==================== SPENDING BY CATEGORY ====================
    spend_by_category = (
        user_df[user_df['Debit'] > 0]
        .groupby('Category')['Debit']
        .sum()
        .reset_index()
        .sort_values('Debit', ascending=False)
        .rename(columns={'Debit': 'amount', 'Category': 'category'})
    )
    
    # ==================== TOP 10 LARGEST TRANSACTIONS ====================
    top_10_transactions = (
        user_df[user_df['Debit'] > 0]
        .nlargest(10, 'Debit')[['Date', 'Description', 'Debit']]
        .reset_index(drop=True)
    )
    
    # Format for frontend
    top_10_largest_transactions = [
        {
            "amount": float(row['Debit']),
            "desc": str(row['Description']),
            "date": row['Date'].strftime('%Y-%m-%d')
        }
        for _, row in top_10_transactions.iterrows()
    ]
    
    # ==================== SPENDING BEHAVIOUR PATTERNS ====================
    
    # Weekend vs Weekday spending
    weekend_spend = user_df[user_df['IsWeekend'] == 1]['Debit'].sum()
    weekday_spend = user_df[user_df['IsWeekend'] == 0]['Debit'].sum()
    weekend_txns = len(user_df[user_df['IsWeekend'] == 1])
    weekday_txns = len(user_df[user_df['IsWeekend'] == 0])
    weekend_avg = weekend_spend / weekend_txns if weekend_txns > 0 else 0
    weekday_avg = weekday_spend / weekday_txns if weekday_txns > 0 else 0
    
    # Monthly spending stats
    monthly_exp = user_df.groupby(user_df['Date'].dt.to_period('M'))['Debit'].sum()
    most_expensive_month = {
        "month": str(monthly_exp.idxmax()),
        "amount": float(monthly_exp.max())
    }
    cheapest_month = {
        "month": str(monthly_exp.idxmin()),
        "amount": float(monthly_exp.min())
    }
    avg_monthly = float(monthly_exp.mean())
    std_deviation = float(monthly_exp.std())
    
    # Transaction size distribution
    bins = [0, 500, 2000, 10000, 50000, float('inf')]
    labels = ['Micro (0-500)', 'Small (501-2K)', 'Medium (2K-10K)', 'Large (10K-50K)', 'Very Large (50K+)']
    debit_only = user_df[user_df['Debit'] > 0].copy()
    debit_only['TxnSize'] = pd.cut(debit_only['Debit'], bins=bins, labels=labels)
    txn_dist = debit_only['TxnSize'].value_counts().sort_index()
    
    size_distribution = [
        {
            "bucket": label.split(' (')[0],
            "range": label.split(' (')[1].replace(')', ''),
            "count": int(count),
            "total": float(debit_only[debit_only['TxnSize'] == label]['Debit'].sum())
        }
        for label, count in txn_dist.items()
    ]
    
    # Category consistency across months
    total_months = user_df['YearMonth'].nunique()
    cat_months = user_df.groupby('Category')['YearMonth'].nunique().sort_values(ascending=False)
    
    category_consistency = [
        {
            "category": cat,
            "consistency_pct": round((months / total_months * 100), 1)
        }
        for cat, months in cat_months.items()
    ]
    
    # ==================== COMBINE RESULTS ====================
    return {
        "spendByCategory": [
            {"category": row["category"], "amount": float(row["amount"])}
            for _, row in spend_by_category.iterrows()
        ],
        "top10LargestTransactions": top_10_largest_transactions,
        "behaviour": {
            "weekendTotal": float(weekend_spend),
            "weekdayTotal": float(weekday_spend),
            "weekendAvg": float(weekend_avg),
            "weekdayAvg": float(weekday_avg),
            "mostExpensiveMonth": most_expensive_month,
            "cheapestMonth": cheapest_month,
            "avgMonthlySpend": float(avg_monthly),
            "stdDeviation": float(std_deviation),
            "sizeDistribution": size_distribution,
            "categoryConsistency": category_consistency
        }
    }


def get_category_spending_breakdown(user_name: str) -> dict:
    """
    Detailed spending breakdown by category with statistics.
    """
    user_df = load_user_dataframe(user_name)
    user_df = user_df.copy()
    
    # Filter only debit transactions
    debit_df = user_df[user_df['Debit'] > 0]
    
    if debit_df.empty:
        return {"categories": [], "summary": {}}
    
    # Category-wise statistics
    category_stats = debit_df.groupby('Category').agg(
        Transactions=('Debit', 'count'),
        Total_Spent=('Debit', 'sum'),
        Avg_Per_Txn=('Debit', 'mean'),
        Max_Txn=('Debit', 'max'),
        Min_Txn=('Debit', 'min')
    ).round(2)
    
    # Calculate percentage of total spend
    total_spent = debit_df['Debit'].sum()
    category_stats['%_of_Total'] = (category_stats['Total_Spent'] / total_spent * 100).round(1)
    
    # Convert to list for frontend
    categories = []
    for category, stats in category_stats.iterrows():
        categories.append({
            "category": category,
            "transactions": int(stats['Transactions']),
            "totalSpent": float(stats['Total_Spent']),
            "avgPerTxn": float(stats['Avg_Per_Txn']),
            "maxTxn": float(stats['Max_Txn']),
            "minTxn": float(stats['Min_Txn']),
            "percentOfTotal": float(stats['%_of_Total'])
        })
    
    # Sort by total spent descending
    categories.sort(key=lambda x: x['totalSpent'], reverse=True)
    
    # Overall summary
    summary = {
        "totalSpent": float(total_spent),
        "totalTransactions": len(debit_df),
        "avgSpendPerTxn": float(debit_df['Debit'].mean()),
        "mostActiveCategory": categories[0]['category'] if categories else None,
        "uniqueCategories": len(categories)
    }
    
    return {
        "categories": categories,
        "summary": summary
    }


def get_spending_trends(user_name: str, period: str = 'monthly') -> dict:
    """
    Get spending trends over time (monthly or weekly).
    """
    user_df = load_user_dataframe(user_name)
    user_df = user_df.copy()
    user_df['Date'] = pd.to_datetime(user_df['Date'])
    
    # Filter debit transactions
    debit_df = user_df[user_df['Debit'] > 0].copy()
    
    if debit_df.empty:
        return {"trends": [], "summary": {}}
    
    # Group by period
    if period == 'monthly':
        debit_df['Period'] = debit_df['Date'].dt.to_period('M')
        period_col = 'Period'
    elif period == 'weekly':
        debit_df['Period'] = debit_df['Date'].dt.to_period('W')
        period_col = 'Period'
    else:
        period = 'daily'
        debit_df['Period'] = debit_df['Date'].dt.date
        period_col = 'Period'
    
    # Aggregate spending by period
    trends = (
        debit_df.groupby(period_col)
        .agg(
            totalSpent=('Debit', 'sum'),
            transactionCount=('Debit', 'count'),
            avgSpend=('Debit', 'mean')
        )
        .reset_index()
        .sort_values(period_col)
    )
    
    # Convert period to string
    trends['period'] = trends[period_col].astype(str)
    
    # Calculate rolling averages
    trends['rollingAvg'] = trends['totalSpent'].rolling(window=3, min_periods=1).mean()
    
    # Format for frontend
    trend_data = [
        {
            "period": row['period'],
            "totalSpent": float(row['totalSpent']),
            "transactionCount": int(row['transactionCount']),
            "avgSpend": float(row['avgSpend']),
            "rollingAvg": float(row['rollingAvg'])
        }
        for _, row in trends.iterrows()
    ]
    
    # Summary statistics
    summary = {
        "period": period,
        "avgSpend": float(trends['totalSpent'].mean()),
        "maxSpend": float(trends['totalSpent'].max()),
        "minSpend": float(trends['totalSpent'].min()),
        "totalPeriods": len(trends),
        "trendDirection": "increasing" if trends['totalSpent'].iloc[-1] > trends['totalSpent'].iloc[0] else "decreasing"
    }
    
    return {
        "trends": trend_data,
        "summary": summary
    }


def get_financial_leakage_analysis(user_name: str) -> dict:
    """
    Analyze financial leakage (non-productive spending).
    """
    user_df = load_user_dataframe(user_name)
    user_df = user_df.copy()
    
    # Define leakage categories
    leakage_categories = ['Betting', 'Charges', 'SMS Charges', 'Card Maintenance', 'Tax']
    productive_categories = ['Savings', 'Data Purchase', 'Airtime', 'Electricity', 'School']
    
    # Filter debit transactions
    debit_df = user_df[user_df['Debit'] > 0]
    
    if debit_df.empty:
        return {"leakage": {}, "breakdown": {}}
    
    total_spent = debit_df['Debit'].sum()
    
    # Calculate leakage
    leakage_df = debit_df[debit_df['Category'].isin(leakage_categories)]
    leakage_amount = leakage_df['Debit'].sum()
    leakage_percentage = (leakage_amount / total_spent * 100) if total_spent > 0 else 0
    
    # Leakage by category
    leakage_by_category = (
        leakage_df.groupby('Category')['Debit']
        .sum()
        .reset_index()
        .sort_values('Debit', ascending=False)
    )
    
    leakage_breakdown = [
        {
            "category": row['Category'],
            "amount": float(row['Debit']),
            "percentage": float((row['Debit'] / total_spent * 100) if total_spent > 0 else 0),
            "transactionCount": len(leakage_df[leakage_df['Category'] == row['Category']])
        }
        for _, row in leakage_by_category.iterrows()
    ]
    
    # Productive spending
    productive_df = debit_df[debit_df['Category'].isin(productive_categories)]
    productive_amount = productive_df['Debit'].sum()
    
    # Other spending breakdown
    p2p_amount = debit_df[debit_df['Category'] == 'P2P Transfer']['Debit'].sum()
    pos_amount = debit_df[debit_df['Category'] == 'POS Transaction']['Debit'].sum()
    other_amount = total_spent - leakage_amount - productive_amount - p2p_amount - pos_amount
    
    spending_breakdown = [
        {"type": "P2P Transfers", "amount": float(p2p_amount)},
        {"type": "POS Purchases", "amount": float(pos_amount)},
        {"type": "Productive", "amount": float(productive_amount)},
        {"type": "Leakage", "amount": float(leakage_amount)},
        {"type": "Other", "amount": float(max(other_amount, 0))}
    ]
    
    # Filter out zero amounts
    spending_breakdown = [item for item in spending_breakdown if item["amount"] > 0]
    
    return {
        "leakage": {
            "totalAmount": float(leakage_amount),
            "percentage": float(leakage_percentage),
            "transactionCount": len(leakage_df),
            "breakdown": leakage_breakdown
        },
        "breakdown": spending_breakdown
    }