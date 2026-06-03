import pandas as pd
from utils.data_loader import load_user_dataframe


def _format_month(period_value: str) -> str:
    parsed = pd.Period(period_value, freq="M").to_timestamp()
    return parsed.strftime("%b %y")


def _round(value: float, digits: int = 2) -> float:
    if pd.isna(value):
        return 0.0
    return round(float(value), digits)


def get_filtered_pie_chart(user_name: str, filter_by: str, period: str) -> dict:
    user_df = load_user_dataframe(user_name)
    user_df = user_df.copy()
    user_df['YearMonth'] = user_df['Date'].dt.to_period('M')
    user_df['YearWeek'] = user_df['Date'].dt.to_period('W')

    # Filter by period
    if filter_by == 'month':
        available = sorted([str(p) for p in user_df['YearMonth'].unique()])
        if period == 'all' or period not in available:
            subset = user_df
            current_period = None
        else:
            subset = user_df[user_df['YearMonth'].astype(str) == period]
            current_period = period
    elif filter_by == 'week':
        available = sorted([str(p) for p in user_df['YearWeek'].unique()])
        if period == 'all' or period not in available:
            subset = user_df
            current_period = None
        else:
            subset = user_df[user_df['YearWeek'].astype(str) == period]
            current_period = period
    else:
        available = []
        subset = user_df
        current_period = None

    # Get category spend for current subset
    cat_spend = subset.groupby('Category')['Debit'].sum().sort_values(ascending=False)

    # Comparison Breakdown: current vs previous period
    # Always show comparison - if "all" selected, compare latest period vs previous
    comparison_breakdown = []
    comparison_period_label = ""

    if filter_by == 'month':
        all_months = sorted([str(p) for p in user_df['YearMonth'].unique()])
        if len(all_months) >= 2:
            if current_period and current_period in all_months:
                current_idx = all_months.index(current_period)
                current_p = current_period
            else:
                # "all" selected - use latest month
                current_idx = len(all_months) - 1
                current_p = all_months[current_idx]

            if current_idx > 0:
                previous_p = all_months[current_idx - 1]
                current_subset = user_df[user_df['YearMonth'].astype(str) == current_p]
                previous_subset = user_df[user_df['YearMonth'].astype(str) == previous_p]
                current_cat_spend = current_subset.groupby('Category')['Debit'].sum()
                previous_cat_spend = previous_subset.groupby('Category')['Debit'].sum()

                all_categories = sorted(set(current_cat_spend.index).union(set(previous_cat_spend.index)))
                comparison_breakdown = [
                    {
                        "category": cat,
                        "current": _round(current_cat_spend.get(cat, 0)),
                        "previous": _round(previous_cat_spend.get(cat, 0)),
                    }
                    for cat in all_categories
                ]
                comparison_period_label = f"{_format_month(current_p)} vs {_format_month(previous_p)}"

    elif filter_by == 'week':
        all_weeks = sorted([str(p) for p in user_df['YearWeek'].unique()])
        if len(all_weeks) >= 2:
            if current_period and current_period in all_weeks:
                current_idx = all_weeks.index(current_period)
                current_p = current_period
            else:
                current_idx = len(all_weeks) - 1
                current_p = all_weeks[current_idx]

            if current_idx > 0:
                previous_p = all_weeks[current_idx - 1]
                current_subset = user_df[user_df['YearWeek'].astype(str) == current_p]
                previous_subset = user_df[user_df['YearWeek'].astype(str) == previous_p]
                current_cat_spend = current_subset.groupby('Category')['Debit'].sum()
                previous_cat_spend = previous_subset.groupby('Category')['Debit'].sum()

                all_categories = sorted(set(current_cat_spend.index).union(set(previous_cat_spend.index)))
                comparison_breakdown = [
                    {
                        "category": cat,
                        "current": _round(current_cat_spend.get(cat, 0)),
                        "previous": _round(previous_cat_spend.get(cat, 0)),
                    }
                    for cat in all_categories
                ]
                comparison_period_label = f"{current_p} vs {previous_p}"

    # Monthly Pie Grid: last 6 months
    monthly_pie_grid = []
    for month_period in user_df['YearMonth'].sort_values().unique()[-6:]:
        month_subset = user_df[user_df['YearMonth'] == month_period]
        month_cat_spend = month_subset.groupby('Category')['Debit'].sum().sort_values(ascending=False)
        monthly_pie_grid.append(
            {
                "month": _format_month(str(month_period)),
                "slices": [
                    {"category": cat, "amount": _round(amount)}
                    for cat, amount in month_cat_spend.items()
                ],
            }
        )

    return {
        "availableMonths": sorted([str(p) for p in user_df['YearMonth'].unique()]),
        "availableWeeks": sorted([str(p) for p in user_df['YearWeek'].unique()]),
        "categoryBreakdown": [
            {"category": cat, "amount": _round(amount)}
            for cat, amount in cat_spend.items()
        ],
        "comparisonBreakdown": comparison_breakdown,
        "comparisonPeriodLabel": comparison_period_label,
        "monthlyPieGrid": monthly_pie_grid,
    }
