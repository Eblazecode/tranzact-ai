// Dashboard data context — all values here MUST be replaced with backend API calls.
// Frontend renders backend JSON only. Placeholder values exist solely so the UI
// renders during development and must be removed once the backend is wired.
// TODO: replace with API call — this entire file should fetch from backend

// API endpoints to integrate:
// GET /your-insights/spending-analysis/{user_name}
// GET /your-insights/predictions/monthly (POST with user_name, predict_year, predict_month_num)
// GET /your-insights/predictions/categories (POST with user_name, predict_year, predict_month_num)
// GET /your-insights/recommendations/{user_name}

export interface DashboardData {
  // Identity / range
  userName: string;
  userInitials: string;
  startDate: string;
  endDate: string;

  // ===== Full Spending Analysis =====
  fsa: {
    transactionCount: number;
    totalSpent: number;
    totalReceived: number;
    netPosition: number;
    highestSpendingMonth: { month: string; amount: number };
    lowestSpendingMonth: { month: string; amount: number };
    highestBalance: { amount: number; date: string };
    lowestBalance: { amount: number; date: string };
    currentBalance: number;
    highestSpendingCategory: { name: string; amount: number };
    spendByCategory: { category: string; amount: number }[];
    monthlyIncomeVsExpenses: { month: string; income: number; expenses: number }[];
    transactionCountByCategory: { category: string; count: number }[];
    dailySpendingTrend: { date: string; amount: number }[];
    spendingByDayOfWeek: { day: string; amount: number }[];
    top10LargestTransactions: { desc: string; amount: number; date: string }[];
    dateRangeText: string;
    summaryNotes: string;
  };

  // ===== Detailed Category Breakdown =====
  categoryBreakdown: {
    rows: {
      category: string;
      transactionCount: number;
      totalSpent: number;
      avgPerTransaction: number;
      maxTransaction: number;
      pctOfTotal: number;
    }[];
    avgDailySpend: number;
    avgMonthlySpend: number;
    mostActiveCategory: string;
  };

  // ===== Financial Health Summary =====
  health: {
    totalIncome: number;
    totalExpenses: number;
    netSavings: number;
    savingsRatePct: number;
    healthStatus: "Healthy" | "Moderate" | "At Risk" | "Critical";
    healthNarrative: string;
    healthScore: number; // out of 85
  };

  // ===== Monthly Financial Flow & Savings Rate =====
  monthlyFlow: {
    monthlyNetSavings: { month: string; netSavings: number }[];
    monthlySavingsRate: { month: string; ratePct: number }[];
    thresholdExplanation: string;
    healthyThresholdNote: string;
  };

  // ===== Spending Behaviour Patterns =====
  behaviour: {
    weekendTotal: number;
    weekdayTotal: number;
    weekendAvg: number;
    weekdayAvg: number;
    mostExpensiveMonth: { month: string; amount: number };
    cheapestMonth: { month: string; amount: number };
    avgMonthlySpend: number;
    stdDeviation: number;
    sizeDistribution: { bucket: "Micro" | "Small" | "Medium" | "Large" | "Very Large"; range: string; count: number; total: number }[];
    categoryConsistency: { category: string; consistencyPct: number }[];
  };

  // ===== Financial Leakage =====
  leakage: {
    totalLeakageAmount: number;
    leakagePct: number;
    leakageTransactionCount: number;
    breakdown: { category: string; amount: number; count: number; avg: number }[];
    bucketBreakdown: { bucket: string; amount: number }[]; // Productive / Leakage / P2P / POS / Other
    amountByCategory: { category: string; amount: number }[];
  };

  // ===== Filtered Pie Chart =====
  filteredPie: {
    availableMonths: string[];
    availableWeeks: string[];
    categoryBreakdown: { category: string; amount: number }[];
    comparisonBreakdown: { category: string; current: number; previous: number }[];
    comparisonPeriodLabel?: string;
    monthlyPieGrid: { month: string; slices: { category: string; amount: number }[] }[];
  };

  // ===== Who You Send Money To =====
  recipients: {
    availableMonths: string[];
    availableWeeks: string[];
    availableYears: string[];
    table: { name: string; frequency: number; totalSent: number }[];
    transferCountByRecipient: { name: string; count: number }[];
    amountSentByRecipient: { name: string; amount: number }[];
  };

  // ===== Anomaly Detection =====
  anomaly: {
    flaggedMonths: { month: string; zScore: number; amount: number }[];
    flaggedWeeks: { week: string; zScore: number; amount: number }[];
    monthlySeries: { month: string; amount: number; isAnomaly: boolean }[];
    weeklySeries: { week: string; amount: number; isAnomaly: boolean }[];
  };

  // ===== Balance Trajectory =====
  balance: {
    startingBalance: number;
    endingBalance: number;
    peakBalance: { amount: number; date: string };
    lowestBalance: { amount: number; date: string };
    avgBalance: number;
    dangerZoneDays: number;
    dailyClosing: { date: string; balance: number }[];
    rolling30Day: { date: string; balance: number }[];
    monthlyAverage: { month: string; avgBalance: number }[];
    monthOverMonthChange: { month: string; change: number }[];
  };

  // ===== Recurring Transactions =====
  recurring: {
    rows: {
      description: string;
      frequencyPct: number;
      monthsRepeated: number;
      totalMonths: number;
      avgAmount: number;
    }[];
    patternSummary: string;
  };

  // ===== Monthly Prediction + XAI =====
  monthlyPredictionXai: {
    startingBaseline: number;
    aiForecast: number;
    actualSpend: number | null;
    forecastError: number;
    lastKnownMonth: string;
    // legacy aliases (kept for compatibility)
    forecastAmount: number;
    baselineAmount: number;
    topUpFactors: { label: string; value: number }[]; // top 3
    topDownFactors: { label: string; value: number }[]; // top 3
    shapWaterfall: { label: string; value: number; direction: "up" | "down" }[];
    spendingDna: { label: string; importance: number }[];
  };

  // ===== Category-wise Prediction + XAI =====
  categoryPredictionXai: {
    categoryName: string;
    predictedSpend: number;
    startingBaseline: number;
    aiForecast: number;
    actualSpend: number | null;
    forecastError: number;
    lastKnownMonth: string;
    topUpFactors: { label: string; value: number }[];
    topDownFactors: { label: string; value: number }[];
    shapWaterfall: { label: string; value: number; direction: "up" | "down" }[];
  }[];

  // ===== AI Recommendations =====
  aiRecommendations: {
    user: string;
    healthScore: number;
    healthScoreMax: number;
    riskStatus: "HEALTHY" | "MODERATE" | "AT RISK" | "CRITICAL";
    totalIncome: number;
    totalSpending: number;
    savingsRatePct: number;
    leakageAmount: number;
    leakagePct: number;
    topCategoryName: string;
    topCategoryAmount: number;
    topCategoryPct: number;
    anomalyStatus: string;
    cards: { id: string; number: number; text: string }[];
  };
}

export const FEATURE_LABELS: Record<string, string> = {
  Month_Index: "Position in data timeline (month no.)",
  Month_Num: "Calendar month (Jan=1 ... Dec=12)",
  Total_Received: "Total money received this month",
  Avg_Balance: "Average account balance this month",
  Unique_Categories: "Number of unique spending categories",
  Transaction_Count: "Total number of transactions",
  Spent_Lag1: "How much was spent last month",
  Spent_Lag2: "How much was spent 2 months ago",
  Received_Lag1: "How much was received last month",
  Spent_Rolling3: "3-month average spending",
  Spend_Momentum: "Month-on-month change in spending",
};

// TODO: replace with API call — every field below must be returned from backend
export function getPlaceholderData(): DashboardData {
  const months = ["Apr 24","May 24","Jun 24","Jul 24","Aug 24","Sep 24","Oct 24","Nov 24","Dec 24","Jan 25","Feb 25","Mar 25"];
  return {
    userName: "Dashboard User",
    userInitials: "IK",
    startDate: "20 Mar 2024",
    endDate: "20 Mar 2025",

    fsa: {
      transactionCount: 482,
      totalSpent: 4779800,
      totalReceived: 5120000,
      netPosition: 340200,
      highestSpendingMonth: { month: "Dec 2024", amount: 980000 },
      lowestSpendingMonth: { month: "Apr 2024", amount: 410000 },
      highestBalance: { amount: 3100000, date: "12 Dec 2024" },
      lowestBalance: { amount: 84000, date: "27 Feb 2025" },
      currentBalance: 2847500,
      highestSpendingCategory: { name: "P2P Transfer", amount: 1932062 },
      spendByCategory: [
        { category: "P2P Transfer", amount: 1932062 },
        { category: "Food & Dining", amount: 685000 },
        { category: "Transport", amount: 542000 },
        { category: "Airtime/Data", amount: 367000 },
        { category: "Bills", amount: 295000 },
        { category: "POS", amount: 412000 },
        { category: "Betting", amount: 254000 },
        { category: "Charges", amount: 47500 },
      ],
      monthlyIncomeVsExpenses: months.map((m, i) => ({
        month: m,
        income: 380000 + (i % 4) * 70000 + i * 15000,
        expenses: 350000 + (i % 5) * 80000 + i * 12000,
      })),
      transactionCountByCategory: [
        { category: "P2P Transfer", count: 142 },
        { category: "Food & Dining", count: 98 },
        { category: "Transport", count: 76 },
        { category: "Airtime/Data", count: 54 },
        { category: "Bills", count: 32 },
        { category: "POS", count: 48 },
        { category: "Betting", count: 22 },
        { category: "Charges", count: 10 },
      ],
      dailySpendingTrend: Array.from({ length: 30 }, (_, i) => ({
        date: `Day ${i + 1}`,
        amount: 8000 + Math.round(Math.sin(i / 2) * 6000) + (i % 4) * 2500,
      })),
      spendingByDayOfWeek: [
        { day: "Mon", amount: 95000 },
        { day: "Tue", amount: 78000 },
        { day: "Wed", amount: 112000 },
        { day: "Thu", amount: 88000 },
        { day: "Fri", amount: 145000 },
        { day: "Sat", amount: 167000 },
        { day: "Sun", amount: 134000 },
      ],
      top10LargestTransactions: [
        { desc: "Transfer to Property Agent", amount: 350000, date: "12 Jan 2025" },
        { desc: "School Fees Payment", amount: 280000, date: "5 Sep 2024" },
        { desc: "Salary Credit", amount: 215000, date: "12 Mar 2025" },
        { desc: "Transfer to Adeyemi O.", amount: 180000, date: "14 Feb 2025" },
        { desc: "POS - Electronics Mart", amount: 145000, date: "8 Dec 2024" },
        { desc: "Transfer to Savings", amount: 120000, date: "30 Nov 2024" },
        { desc: "Hotel Booking", amount: 95000, date: "22 Dec 2024" },
        { desc: "Flight Ticket - Lagos/Abuja", amount: 88000, date: "10 Oct 2024" },
        { desc: "Furniture Purchase", amount: 76000, date: "3 Aug 2024" },
        { desc: "Medical Bill", amount: 65000, date: "15 Jul 2024" },
      ],
      dateRangeText: "Statement covers 12 months from 20 Mar 2024 to 20 Mar 2025.",
      summaryNotes: "Across the period analysed, total inflows slightly exceed outflows giving a marginally positive net position. Spending is dominated by P2P transfers which account for the largest share of debits. December was the heaviest spending month while April was the lightest.",
    },

    categoryBreakdown: {
      rows: [
        { category: "P2P Transfer", transactionCount: 142, totalSpent: 1932062, avgPerTransaction: 13606, maxTransaction: 350000, pctOfTotal: 40.4 },
        { category: "Food & Dining", transactionCount: 98, totalSpent: 685000, avgPerTransaction: 6989, maxTransaction: 28500, pctOfTotal: 14.3 },
        { category: "Transport", transactionCount: 76, totalSpent: 542000, avgPerTransaction: 7131, maxTransaction: 18000, pctOfTotal: 11.3 },
        { category: "POS", transactionCount: 48, totalSpent: 412000, avgPerTransaction: 8583, maxTransaction: 145000, pctOfTotal: 8.6 },
        { category: "Airtime/Data", transactionCount: 54, totalSpent: 367000, avgPerTransaction: 6796, maxTransaction: 15000, pctOfTotal: 7.7 },
        { category: "Bills", transactionCount: 32, totalSpent: 295000, avgPerTransaction: 9218, maxTransaction: 42000, pctOfTotal: 6.2 },
        { category: "Betting", transactionCount: 22, totalSpent: 254000, avgPerTransaction: 11545, maxTransaction: 50000, pctOfTotal: 5.3 },
        { category: "Charges", transactionCount: 10, totalSpent: 47500, avgPerTransaction: 4750, maxTransaction: 12000, pctOfTotal: 1.0 },
      ],
      avgDailySpend: 13095,
      avgMonthlySpend: 398316,
      mostActiveCategory: "P2P Transfer",
    },

    health: {
      totalIncome: 5120000,
      totalExpenses: 4779800,
      netSavings: 340200,
      savingsRatePct: 6.6,
      healthStatus: "Moderate",
      healthNarrative:
        "Your overall financial health is moderate. You earn slightly more than you spend across the period but the buffer is thin. P2P transfer activity dominates outflows and savings rate sits below the recommended 20% threshold.",
      healthScore: 52,
    },

    monthlyFlow: {
      monthlyNetSavings: months.map((m, i) => ({
        month: m,
        netSavings: [120000, 95000, -40000, 65000, 80000, 110000, 130000, 85000, -45000, 60000, -120000, 30000][i],
      })),
      monthlySavingsRate: months.map((m, i) => ({
        month: m,
        ratePct: [22.4, 18.1, -8.2, 13.5, 14.7, 19.6, 16.7, 12.0, -5.5, 7.1, -15.8, 5.6][i],
      })),
      thresholdExplanation:
        "A healthy savings rate sits at 20% or higher. Rates between 10-20% are acceptable but leave little margin for emergencies. Anything below 10% (or negative) signals overspending relative to income.",
      healthyThresholdNote: "Healthy threshold: ≥ 20%",
    },

    behaviour: {
      weekendTotal: 1812000,
      weekdayTotal: 2967800,
      weekendAvg: 17423,
      weekdayAvg: 9728,
      mostExpensiveMonth: { month: "Dec 2024", amount: 980000 },
      cheapestMonth: { month: "Apr 2024", amount: 410000 },
      avgMonthlySpend: 398316,
      stdDeviation: 168200,
      sizeDistribution: [
        { bucket: "Micro", range: "< ₦500", count: 64, total: 18200 },
        { bucket: "Small", range: "₦500 – ₦2,000", count: 142, total: 184500 },
        { bucket: "Medium", range: "₦2,000 – ₦10,000", count: 198, total: 1124000 },
        { bucket: "Large", range: "₦10,000 – ₦50,000", count: 64, total: 1582000 },
        { bucket: "Very Large", range: "> ₦50,000", count: 14, total: 1871100 },
      ],
      categoryConsistency: [
        { category: "Airtime/Data", consistencyPct: 92 },
        { category: "Bills", consistencyPct: 85 },
        { category: "Transport", consistencyPct: 78 },
        { category: "Food & Dining", consistencyPct: 71 },
        { category: "P2P Transfer", consistencyPct: 64 },
        { category: "POS", consistencyPct: 48 },
        { category: "Betting", consistencyPct: 32 },
      ],
    },

    leakage: {
      totalLeakageAmount: 47500,
      leakagePct: 1.0,
      leakageTransactionCount: 34,
      breakdown: [
        { category: "USSD Transaction Fees", amount: 15000, count: 15, avg: 1000 },
        { category: "SMS Alert Charges", amount: 12000, count: 12, avg: 1000 },
        { category: "Stamp Duty Charges", amount: 12000, count: 3, avg: 4000 },
        { category: "Card Maintenance Fee", amount: 8500, count: 4, avg: 2125 },
      ],
      bucketBreakdown: [
        { bucket: "Productive", amount: 1850000 },
        { bucket: "Leakage", amount: 47500 },
        { bucket: "P2P Transfer", amount: 1932062 },
        { bucket: "POS", amount: 412000 },
        { bucket: "Other", amount: 538238 },
      ],
      amountByCategory: [
        { category: "USSD Fees", amount: 15000 },
        { category: "SMS Alerts", amount: 12000 },
        { category: "Stamp Duty", amount: 12000 },
        { category: "Card Fees", amount: 8500 },
      ],
    },

    filteredPie: {
      availableMonths: ["All", ...months],
      availableWeeks: ["All", "Week 1", "Week 2", "Week 3", "Week 4", "Week 5"],
      comparisonPeriodLabel: "Previous Period",
      categoryBreakdown: [
        { category: "P2P Transfer", amount: 320000 },
        { category: "Food & Dining", amount: 142000 },
        { category: "Transport", amount: 95000 },
        { category: "Airtime/Data", amount: 67000 },
        { category: "Bills", amount: 48000 },
        { category: "POS", amount: 38000 },
      ],
      comparisonBreakdown: [
        { category: "P2P Transfer", current: 320000, previous: 280000 },
        { category: "Food & Dining", current: 142000, previous: 158000 },
        { category: "Transport", current: 95000, previous: 88000 },
        { category: "Airtime/Data", current: 67000, previous: 72000 },
        { category: "Bills", current: 48000, previous: 45000 },
      ],
      monthlyPieGrid: months.slice(-6).map((m) => ({
        month: m,
        slices: [
          { category: "P2P Transfer", amount: 250000 + Math.round(Math.random() * 80000) },
          { category: "Food", amount: 90000 + Math.round(Math.random() * 40000) },
          { category: "Transport", amount: 60000 + Math.round(Math.random() * 30000) },
          { category: "Airtime", amount: 35000 + Math.round(Math.random() * 15000) },
          { category: "Bills", amount: 25000 + Math.round(Math.random() * 20000) },
        ],
      })),
    },

    recipients: {
      availableMonths: ["All", ...months],
      availableWeeks: ["All", "Week 1", "Week 2", "Week 3", "Week 4"],
      availableYears: ["All", "2024", "2025"],
      table: [
        { name: "Adeyemi O.", frequency: 15, totalSent: 380000 },
        { name: "Favour E.", frequency: 12, totalSent: 185000 },
        { name: "MTN Nigeria", frequency: 10, totalSent: 95000 },
        { name: "Bolt Rides", frequency: 8, totalSent: 67000 },
        { name: "Property Agent", frequency: 3, totalSent: 450000 },
        { name: "Shoprite", frequency: 6, totalSent: 88000 },
      ],
      transferCountByRecipient: [
        { name: "Adeyemi O.", count: 15 },
        { name: "Favour E.", count: 12 },
        { name: "MTN Nigeria", count: 10 },
        { name: "Bolt Rides", count: 8 },
        { name: "Shoprite", count: 6 },
      ],
      amountSentByRecipient: [
        { name: "Property Agent", amount: 450000 },
        { name: "Adeyemi O.", amount: 380000 },
        { name: "Favour E.", amount: 185000 },
        { name: "MTN Nigeria", amount: 95000 },
        { name: "Shoprite", amount: 88000 },
      ],
    },

    anomaly: {
      flaggedMonths: [
        { month: "Dec 2024", zScore: 2.4, amount: 980000 },
        { month: "Feb 2025", zScore: -2.1, amount: 200000 },
      ],
      flaggedWeeks: [
        { week: "Week of 9 Dec 2024", zScore: 2.8, amount: 285000 },
      ],
      monthlySeries: months.map((m, i) => {
        const amount = [410000, 460000, 520000, 480000, 510000, 545000, 590000, 620000, 980000, 590000, 200000, 670000][i];
        return { month: m, amount, isAnomaly: m === "Dec 24" || m === "Feb 25" };
      }),
      weeklySeries: Array.from({ length: 12 }, (_, i) => {
        const amount = 95000 + Math.round(Math.sin(i / 2) * 40000) + (i % 3) * 20000;
        return { week: `W${i + 1}`, amount: i === 8 ? 285000 : amount, isAnomaly: i === 8 };
      }),
    },

    balance: {
      startingBalance: 2100000,
      endingBalance: 2847500,
      peakBalance: { amount: 3100000, date: "12 Dec 2024" },
      lowestBalance: { amount: 84000, date: "27 Feb 2025" },
      avgBalance: 2570000,
      dangerZoneDays: 14,
      dailyClosing: Array.from({ length: 60 }, (_, i) => ({
        date: `D${i + 1}`,
        balance: 2100000 + Math.round(Math.sin(i / 5) * 400000) + i * 12000,
      })),
      rolling30Day: Array.from({ length: 60 }, (_, i) => ({
        date: `D${i + 1}`,
        balance: 2300000 + i * 9000,
      })),
      monthlyAverage: months.map((m, i) => ({
        month: m,
        avgBalance: 2200000 + i * 50000 + (i % 3) * 60000,
      })),
      monthOverMonthChange: months.map((m, i) => ({
        month: m,
        change: [0, 150000, -70000, 220000, 150000, -250000, 350000, 130000, 200000, -350000, -150000, 247500][i],
      })),
    },

    recurring: {
      rows: [
        { description: "Salary - TechCorp Ltd", frequencyPct: 100, monthsRepeated: 12, totalMonths: 12, avgAmount: 890000 },
        { description: "Netflix Subscription", frequencyPct: 100, monthsRepeated: 12, totalMonths: 12, avgAmount: 6500 },
        { description: "Spotify Premium", frequencyPct: 92, monthsRepeated: 11, totalMonths: 12, avgAmount: 4500 },
        { description: "SMS Alert Fee", frequencyPct: 100, monthsRepeated: 12, totalMonths: 12, avgAmount: 1000 },
        { description: "Card Maintenance", frequencyPct: 33, monthsRepeated: 4, totalMonths: 12, avgAmount: 2125 },
        { description: "Glo Data Bundle", frequencyPct: 83, monthsRepeated: 10, totalMonths: 12, avgAmount: 5000 },
        { description: "Freelance - Fiverr", frequencyPct: 50, monthsRepeated: 6, totalMonths: 12, avgAmount: 215000 },
      ],
      patternSummary:
        "5 strong recurring debits and 2 recurring credits detected. The salary credit is the most consistent inflow. Netflix, SMS alerts and Spotify form a stable monthly outflow of small fixed charges.",
    },

    monthlyPredictionXai: {
      startingBaseline: 670000,
      aiForecast: 815000,
      actualSpend: 840000,
      forecastError: 25000,
      lastKnownMonth: "Mar 2025",
      forecastAmount: 815000,
      baselineAmount: 670000,
      topUpFactors: [
        { label: "Total money received this month", value: 45000 },
        { label: "3-month average spending", value: 38000 },
        { label: "Average account balance this month", value: 18000 },
      ],
      topDownFactors: [
        { label: "How much was spent last month", value: -22000 },
        { label: "Month-on-month change in spending", value: -12000 },
        { label: "How much was received last month", value: -6000 },
      ],
      shapWaterfall: [
        { label: "Total money received this month", value: 45000, direction: "up" },
        { label: "3-month average spending", value: 38000, direction: "up" },
        { label: "How much was spent last month", value: -22000, direction: "down" },
        { label: "Average account balance this month", value: 18000, direction: "up" },
        { label: "Total number of transactions", value: 15000, direction: "up" },
        { label: "Month-on-month change in spending", value: -12000, direction: "down" },
        { label: "Number of unique spending categories", value: 8000, direction: "up" },
        { label: "How much was received last month", value: -6000, direction: "down" },
        { label: "Calendar month (Jan=1 ... Dec=12)", value: 4000, direction: "up" },
        { label: "How much was spent 2 months ago", value: -3000, direction: "down" },
        { label: "Position in data timeline (month no.)", value: 2000, direction: "up" },
      ],
      spendingDna: [
        { label: "Total money received this month", importance: 52000 },
        { label: "3-month average spending", importance: 41000 },
        { label: "How much was spent last month", importance: 35000 },
        { label: "Average account balance this month", importance: 28000 },
        { label: "Total number of transactions", importance: 22000 },
        { label: "Month-on-month change in spending", importance: 18000 },
        { label: "Number of unique spending categories", importance: 12000 },
        { label: "How much was received last month", importance: 9000 },
        { label: "Calendar month (Jan=1 ... Dec=12)", importance: 6000 },
        { label: "How much was spent 2 months ago", importance: 4000 },
        { label: "Position in data timeline (month no.)", importance: 2500 },
      ],
    },

    categoryPredictionXai: [
      {
        categoryName: "Betting",
        predictedSpend: 25400,
        startingBaseline: 19050,
        aiForecast: 25400,
        actualSpend: 26670,
        forecastError: 1270,
        lastKnownMonth: "Mar 2025",
        topUpFactors: [
          { label: "3-month average spending in Betting", value: 8000 },
          { label: "Total money received this month", value: 5400 },
          { label: "Weekend transaction count", value: 3200 },
        ],
        topDownFactors: [
          { label: "Last month spend in Betting", value: -4200 },
          { label: "Average account balance", value: -2800 },
          { label: "Spend in other discretionary categories", value: -1500 },
        ],
        shapWaterfall: [
          { label: "3-month average spending in Betting", value: 8000, direction: "up" },
          { label: "Total money received this month", value: 5400, direction: "up" },
          { label: "Weekend transaction count", value: 3200, direction: "up" },
          { label: "Last month spend in Betting", value: -4200, direction: "down" },
          { label: "Average account balance", value: -2800, direction: "down" },
          { label: "Spend in other discretionary categories", value: -1500, direction: "down" },
        ],
      },
      {
        categoryName: "P2P Transfer",
        predictedSpend: 188200,
        startingBaseline: 141150,
        aiForecast: 188200,
        actualSpend: 197610,
        forecastError: 9410,
        lastKnownMonth: "Mar 2025",
        topUpFactors: [
          { label: "Total money received this month", value: 32000 },
          { label: "3-month average P2P spending", value: 28000 },
          { label: "Number of unique recipients", value: 14000 },
        ],
        topDownFactors: [
          { label: "Last month P2P spend", value: -18000 },
          { label: "Average account balance", value: -9000 },
          { label: "Month-on-month spend momentum", value: -5500 },
        ],
        shapWaterfall: [
          { label: "Total money received this month", value: 32000, direction: "up" },
          { label: "3-month average P2P spending", value: 28000, direction: "up" },
          { label: "Number of unique recipients", value: 14000, direction: "up" },
          { label: "Last month P2P spend", value: -18000, direction: "down" },
          { label: "Average account balance", value: -9000, direction: "down" },
          { label: "Month-on-month spend momentum", value: -5500, direction: "down" },
        ],
      },
      {
        categoryName: "Food & Dining",
        predictedSpend: 72500,
        startingBaseline: 54375,
        aiForecast: 72500,
        actualSpend: 76125,
        forecastError: 3625,
        lastKnownMonth: "Mar 2025",
        topUpFactors: [
          { label: "Weekend day count this month", value: 6500 },
          { label: "3-month average food spending", value: 5800 },
          { label: "Total transaction count", value: 3200 },
        ],
        topDownFactors: [
          { label: "Last month food spend", value: -3800 },
          { label: "Average account balance", value: -2400 },
          { label: "Bills spend this month", value: -1200 },
        ],
        shapWaterfall: [
          { label: "Weekend day count this month", value: 6500, direction: "up" },
          { label: "3-month average food spending", value: 5800, direction: "up" },
          { label: "Total transaction count", value: 3200, direction: "up" },
          { label: "Last month food spend", value: -3800, direction: "down" },
          { label: "Average account balance", value: -2400, direction: "down" },
          { label: "Bills spend this month", value: -1200, direction: "down" },
        ],
      },
      {
        categoryName: "Airtime/Data",
        predictedSpend: 31200,
        startingBaseline: 23400,
        aiForecast: 31200,
        actualSpend: 32760,
        forecastError: 1560,
        lastKnownMonth: "Mar 2025",
        topUpFactors: [
          { label: "3-month average airtime", value: 2400 },
          { label: "Total transaction count", value: 1800 },
          { label: "Weekend transaction count", value: 900 },
        ],
        topDownFactors: [
          { label: "Last month airtime spend", value: -1500 },
          { label: "Average account balance", value: -800 },
          { label: "Total received last month", value: -400 },
        ],
        shapWaterfall: [
          { label: "3-month average airtime", value: 2400, direction: "up" },
          { label: "Total transaction count", value: 1800, direction: "up" },
          { label: "Weekend transaction count", value: 900, direction: "up" },
          { label: "Last month airtime spend", value: -1500, direction: "down" },
          { label: "Average account balance", value: -800, direction: "down" },
          { label: "Total received last month", value: -400, direction: "down" },
        ],
      },
      {
        categoryName: "Bills",
        predictedSpend: 28800,
        startingBaseline: 21600,
        aiForecast: 28800,
        actualSpend: 30240,
        forecastError: 1440,
        lastKnownMonth: "Mar 2025",
        topUpFactors: [
          { label: "3-month average bills", value: 2200 },
          { label: "Calendar month (end of month)", value: 1700 },
          { label: "Total received this month", value: 1100 },
        ],
        topDownFactors: [
          { label: "Last month bills spend", value: -1400 },
          { label: "Average account balance", value: -700 },
          { label: "Other discretionary spend", value: -300 },
        ],
        shapWaterfall: [
          { label: "3-month average bills", value: 2200, direction: "up" },
          { label: "Calendar month (end of month)", value: 1700, direction: "up" },
          { label: "Total received this month", value: 1100, direction: "up" },
          { label: "Last month bills spend", value: -1400, direction: "down" },
          { label: "Average account balance", value: -700, direction: "down" },
          { label: "Other discretionary spend", value: -300, direction: "down" },
        ],
      },
      {
        categoryName: "POS",
        predictedSpend: 42100,
        startingBaseline: 31575,
        aiForecast: 42100,
        actualSpend: 44205,
        forecastError: 2105,
        lastKnownMonth: "Mar 2025",
        topUpFactors: [
          { label: "3-month average POS spend", value: 4200 },
          { label: "Weekend transaction count", value: 2900 },
          { label: "Total transaction count", value: 1700 },
        ],
        topDownFactors: [
          { label: "Last month POS spend", value: -2600 },
          { label: "Average account balance", value: -1200 },
          { label: "Total received last month", value: -500 },
        ],
        shapWaterfall: [
          { label: "3-month average POS spend", value: 4200, direction: "up" },
          { label: "Weekend transaction count", value: 2900, direction: "up" },
          { label: "Total transaction count", value: 1700, direction: "up" },
          { label: "Last month POS spend", value: -2600, direction: "down" },
          { label: "Average account balance", value: -1200, direction: "down" },
          { label: "Total received last month", value: -500, direction: "down" },
        ],
      },
      {
        categoryName: "Charges",
        predictedSpend: 4100,
        startingBaseline: 3075,
        aiForecast: 4100,
        actualSpend: 4305,
        forecastError: 205,
        lastKnownMonth: "Mar 2025",
        topUpFactors: [
          { label: "Total transaction count", value: 600 },
          { label: "Number of POS transactions", value: 380 },
          { label: "USSD transaction count", value: 220 },
        ],
        topDownFactors: [
          { label: "Last month charges", value: -180 },
          { label: "Card status active months", value: -90 },
          { label: "Average balance", value: -50 },
        ],
        shapWaterfall: [
          { label: "Total transaction count", value: 600, direction: "up" },
          { label: "Number of POS transactions", value: 380, direction: "up" },
          { label: "USSD transaction count", value: 220, direction: "up" },
          { label: "Last month charges", value: -180, direction: "down" },
          { label: "Card status active months", value: -90, direction: "down" },
          { label: "Average balance", value: -50, direction: "down" },
        ],
      },
    ],

    aiRecommendations: {
      user: "Dashboard User",
      healthScore: 45,
      healthScoreMax: 85,
      riskStatus: "AT RISK",
      totalIncome: 203234,
      totalSpending: 221688,
      savingsRatePct: -9.1,
      leakageAmount: 200,
      leakagePct: 0.1,
      topCategoryName: "P2P Transfer",
      topCategoryAmount: 193062,
      topCategoryPct: 87.1,
      anomalyStatus: "None detected",
      cards: [
        { id: "r1", number: 1, text: "Reduce discretionary expenses and redirect savings toward an emergency fund equal to at least 3 months of essential spending. Start with cutting back on entertainment and dining-out subscriptions." },
        { id: "r2", number: 2, text: "Create a detailed monthly budget tracking system. Assign every naira a purpose at the start of the month (zero-based budgeting) so unplanned overspending is visible immediately." },
        { id: "r3", number: 3, text: "Reduce betting and card maintenance leakage. The combined small charges add up over the year and silently push your savings rate further into the negative." },
        { id: "r4", number: 4, text: "Review your high P2P transfer activity. P2P accounts for 87.1% of your spending — verify each large recurring recipient is intentional and consider consolidating where possible." },
      ],
    },
  };
}

function zeroizeValue(value: unknown): unknown {
  if (typeof value === "number") return 0;
  if (typeof value === "string") return "";
  if (typeof value === "boolean") return false;
  if (value === null || value === undefined) return value;
  if (Array.isArray(value)) return [];
  if (typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, nested]) => [key, zeroizeValue(nested)]),
    );
  }
  return value;
}

export function getEmptyDashboardData(userName = "Dashboard User"): DashboardData {
  const zeroData = zeroizeValue(getPlaceholderData()) as DashboardData;
  const initials = userName
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("") || "DU";

  return {
    ...zeroData,
    userName,
    userInitials: initials,
    health: {
      ...zeroData.health,
      healthStatus: "Moderate",
    },
    aiRecommendations: {
      ...zeroData.aiRecommendations,
      user: userName,
      riskStatus: "MODERATE",
      anomalyStatus: "None detected",
      cards: [],
    },
  };
}

type HealthApiResponse = {
  total_in: number;
  total_out: number;
  net: number;
  savings_rate: number;
  health: "HEALTHY" | "MODERATE" | "AT RISK" | "CRITICAL";
};

type MonthlyFlowApiResponse = {
  monthly: {
    month: string;
    income: number;
    expense: number;
    savings: number;
    savings_rate: number;
    savings_direction: string;
  }[];
  threshold_explanation: string;
};

type CategoryBreakdownApiResponse = {
  summary: {
    category: string;
    transactions: number;
    total_spent: number;
    avg_per_txn: number;
    max_txn: number;
    percent_of_total_spend: number;
  }[];
  totals: {
    total_spent: number;
    total_received: number;
    net_position: number;
    avg_daily_spend: number;
    avg_monthly_spend: number;
    most_active_category: string;
    most_active_count: number;
  };
  charts: {
    category_spend_bar: { category: string; amount: number }[];
    monthly_income_vs_expenses: { month: string; income: number; expense: number }[];
    transaction_count_by_category: { category: string; count: number }[];
    daily_spending_trend: { date: string; amount: number; rolling_7_day_avg: number }[];
    spending_by_day_of_week: { day: string; amount: number; is_weekend: boolean }[];
    top_10_largest_transactions: { date: string; category: string; description: string; amount: number }[];
  };
};

type DashboardApiResponse = DashboardData;

function normalizeHealthPayload(
  health: Partial<DashboardData["health"]> | null | undefined,
  fallback: DashboardData["health"],
): DashboardData["health"] {
  if (!health) return fallback;

  const rawStatus = String(health.healthStatus ?? fallback.healthStatus).toUpperCase();
  const healthStatus =
    rawStatus === "HEALTHY" ? "Healthy" :
    rawStatus === "MODERATE" ? "Moderate" :
    rawStatus === "AT RISK" ? "At Risk" :
    rawStatus === "CRITICAL" ? "Critical" :
    fallback.healthStatus;

  return {
    totalIncome: Number(health.totalIncome ?? fallback.totalIncome),
    totalExpenses: Number(health.totalExpenses ?? fallback.totalExpenses),
    netSavings: Number(health.netSavings ?? fallback.netSavings),
    savingsRatePct: Number(health.savingsRatePct ?? fallback.savingsRatePct),
    healthStatus,
    healthNarrative: String(health.healthNarrative ?? fallback.healthNarrative),
    healthScore: Number(health.healthScore ?? fallback.healthScore),
  };
}

function normalizeMonthlyFlowPayload(
  monthlyFlow: Record<string, any> | null | undefined,
  fallback: DashboardData["monthlyFlow"],
): DashboardData["monthlyFlow"] {
  if (!monthlyFlow) return fallback;

  if (Array.isArray(monthlyFlow.monthlyNetSavings) && Array.isArray(monthlyFlow.monthlySavingsRate)) {
    return {
      monthlyNetSavings: monthlyFlow.monthlyNetSavings,
      monthlySavingsRate: monthlyFlow.monthlySavingsRate,
      thresholdExplanation: monthlyFlow.thresholdExplanation ?? fallback.thresholdExplanation,
      healthyThresholdNote: monthlyFlow.healthyThresholdNote ?? fallback.healthyThresholdNote,
    };
  }

  if (Array.isArray(monthlyFlow.monthly)) {
    return {
      monthlyNetSavings: monthlyFlow.monthly.map((row: Record<string, any>) => ({
        month: formatMonthLabel(String(row.month ?? "")),
        netSavings: Number(row.savings ?? row.netSavings ?? 0),
      })),
      monthlySavingsRate: monthlyFlow.monthly.map((row: Record<string, any>) => ({
        month: formatMonthLabel(String(row.month ?? "")),
        ratePct: Number(row.savingsRate ?? row.savings_rate ?? row.ratePct ?? 0),
      })),
      thresholdExplanation: String(
        monthlyFlow.thresholdExplanation ??
        monthlyFlow.threshold_explanation ??
        fallback.thresholdExplanation,
      ),
      healthyThresholdNote: String(monthlyFlow.healthyThresholdNote ?? fallback.healthyThresholdNote),
    };
  }

  return fallback;
}

function normalizeCategoryPredictionPayload(
  categoryPrediction: DashboardData["categoryPredictionXai"] | { categories?: DashboardData["categoryPredictionXai"] } | null | undefined,
  fallback: DashboardData["categoryPredictionXai"],
): DashboardData["categoryPredictionXai"] {
  if (Array.isArray(categoryPrediction)) {
    return categoryPrediction;
  }

  if (categoryPrediction && Array.isArray(categoryPrediction.categories)) {
    return categoryPrediction.categories;
  }

  return fallback;
}

function getApiBaseUrl() {
  return getSharedApiBaseUrl();
}

function getStoredUserName() {
  if (typeof window === "undefined") return getPlaceholderData().userName;
  try {
    const raw = localStorage.getItem("transacai_session");
    if (!raw) return getPlaceholderData().userName;
    const parsed = JSON.parse(raw) as { userName?: string };
    return parsed.userName || getPlaceholderData().userName;
  } catch {
    return getPlaceholderData().userName;
  }
}

function titleizeHealthStatus(status: HealthApiResponse["health"]): DashboardData["health"]["healthStatus"] {
  switch (status) {
    case "HEALTHY":
      return "Healthy";
    case "MODERATE":
      return "Moderate";
    case "AT RISK":
      return "At Risk";
    case "CRITICAL":
      return "Critical";
  }
}

function buildHealthNarrative(payload: HealthApiResponse) {
  const rate = payload.savings_rate;
  const status = payload.health;
  if (status === "HEALTHY") {
    return `Your income comfortably exceeds your expenses and your savings rate is ${rate.toFixed(1)}%. This suggests strong spending control and a healthy financial buffer.`;
  }
  if (status === "MODERATE") {
    return `Your income is still ahead of your expenses, but the savings rate of ${rate.toFixed(1)}% leaves limited room for shocks. Tightening discretionary spending would improve resilience.`;
  }
  if (status === "AT RISK") {
    return `You are close to break-even with a savings rate of ${rate.toFixed(1)}%. A small increase in spending or drop in income could push you into negative savings.`;
  }
  return `Your expenses currently exceed your income, producing a savings rate of ${rate.toFixed(1)}%. Immediate spending cuts or income improvements are needed to restore stability.`;
}

function buildHealthScore(payload: HealthApiResponse) {
  const normalized = Math.max(-20, Math.min(40, payload.savings_rate));
  return Math.max(0, Math.min(85, Math.round(((normalized + 20) / 60) * 85)));
}

function formatMonthLabel(value: string) {
  const parsed = new Date(`${value}-01T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleDateString("en-NG", { month: "short", year: "2-digit" });
}

function mergeApiData(
  base: DashboardData,
  category: CategoryBreakdownApiResponse | null,
  health: HealthApiResponse | null,
  monthlyFlow: MonthlyFlowApiResponse | null,
  userName: string,
): DashboardData {
  let next = { ...base, userName, userInitials: userName.split(/\s+/).map((p) => p[0]).slice(0, 2).join("").toUpperCase() };

  if (category) {
    const daily = category.charts.daily_spending_trend;
    const monthlies = category.charts.monthly_income_vs_expenses;
    const highestMonth = [...monthlies].sort((a, b) => b.expense - a.expense)[0];
    const lowestMonth = [...monthlies].sort((a, b) => a.expense - b.expense)[0];
    next = {
      ...next,
      startDate: daily[0]?.date ?? base.startDate,
      endDate: daily[daily.length - 1]?.date ?? base.endDate,
      fsa: {
        ...next.fsa,
        transactionCount: category.summary.reduce((sum, row) => sum + row.transactions, 0),
        totalSpent: category.totals.total_spent,
        totalReceived: category.totals.total_received,
        netPosition: category.totals.net_position,
        highestSpendingMonth: highestMonth
          ? { month: formatMonthLabel(highestMonth.month), amount: highestMonth.expense }
          : next.fsa.highestSpendingMonth,
        lowestSpendingMonth: lowestMonth
          ? { month: formatMonthLabel(lowestMonth.month), amount: lowestMonth.expense }
          : next.fsa.lowestSpendingMonth,
        highestSpendingCategory: category.summary[0]
          ? { name: category.summary[0].category, amount: category.summary[0].total_spent }
          : next.fsa.highestSpendingCategory,
        spendByCategory: category.charts.category_spend_bar,
        monthlyIncomeVsExpenses: monthlies.map((row) => ({
          month: formatMonthLabel(row.month),
          income: row.income,
          expenses: row.expense,
        })),
        transactionCountByCategory: category.charts.transaction_count_by_category,
        dailySpendingTrend: daily.map((row) => ({ date: row.date, amount: row.amount })),
        spendingByDayOfWeek: category.charts.spending_by_day_of_week.map((row) => ({
          day: row.day.slice(0, 3),
          amount: row.amount,
        })),
        top10LargestTransactions: category.charts.top_10_largest_transactions.map((row) => ({
          desc: row.description,
          amount: row.amount,
          date: row.date,
        })),
        dateRangeText: `Statement covers ${daily.length} active days from ${daily[0]?.date ?? next.startDate} to ${daily[daily.length - 1]?.date ?? next.endDate}.`,
        summaryNotes: `Spending is led by ${category.totals.most_active_category}. Total inflows and outflows are now being loaded from the backend for this user.`,
      },
      categoryBreakdown: {
        rows: category.summary.map((row) => ({
          category: row.category,
          transactionCount: row.transactions,
          totalSpent: row.total_spent,
          avgPerTransaction: row.avg_per_txn,
          maxTransaction: row.max_txn,
          pctOfTotal: row.percent_of_total_spend,
        })),
        avgDailySpend: category.totals.avg_daily_spend,
        avgMonthlySpend: category.totals.avg_monthly_spend,
        mostActiveCategory: category.totals.most_active_category,
      },
    };
  }

  if (health) {
    next = {
      ...next,
      health: {
        totalIncome: health.total_in,
        totalExpenses: health.total_out,
        netSavings: health.net,
        savingsRatePct: health.savings_rate,
        healthStatus: titleizeHealthStatus(health.health),
        healthNarrative: buildHealthNarrative(health),
        healthScore: buildHealthScore(health),
      },
    };
  }

  if (monthlyFlow) {
    next = {
      ...next,
      monthlyFlow: {
        monthlyNetSavings: monthlyFlow.monthly.map((row) => ({
          month: formatMonthLabel(row.month),
          netSavings: row.savings,
        })),
        monthlySavingsRate: monthlyFlow.monthly.map((row) => ({
          month: formatMonthLabel(row.month),
          ratePct: row.savings_rate,
        })),
        thresholdExplanation: monthlyFlow.threshold_explanation,
        healthyThresholdNote: "Healthy threshold: >= 20%",
      },
    };
  }

  return next;
}

async function fetchJson<T>(path: string, userName: string): Promise<T> {
  const url = new URL(`${getApiBaseUrl()}${path}`);
  url.searchParams.set("user_name", userName);

  const response = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed for ${path}: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function loadDashboardData(userName = getStoredUserName()): Promise<DashboardData> {
  try {
    const url = `${getApiBaseUrl()}/api/dashboard?user_name=${encodeURIComponent(userName)}`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Dashboard API returned ${response.status}`);
    }

    const d = await response.json() as Record<string, any>;
    if (typeof d.error === "string" && !d.fsa) {
      throw new Error(d.error);
    }

    // Map the full backend payload to DashboardData
    const empty = getEmptyDashboardData(userName);
    const initials = (d.userName || userName).split(/\s+/).map((p: string) => p[0]).slice(0, 2).join("").toUpperCase();

    return {
      userName: d.userName || userName,
      userInitials: d.userInitials || initials,
      startDate: d.startDate || "",
      endDate: d.endDate || "",

      fsa: {
        transactionCount: d.fsa?.transactionCount ?? 0,
        totalSpent: d.fsa?.totalSpent ?? 0,
        totalReceived: d.fsa?.totalReceived ?? 0,
        netPosition: d.fsa?.netPosition ?? 0,
        highestSpendingMonth: d.fsa?.highestSpendingMonth ?? { month: "", amount: 0 },
        lowestSpendingMonth: d.fsa?.lowestSpendingMonth ?? { month: "", amount: 0 },
        highestBalance: d.fsa?.highestBalance ?? { amount: 0, date: "" },
        lowestBalance: d.fsa?.lowestBalance ?? { amount: 0, date: "" },
        currentBalance: d.fsa?.currentBalance ?? 0,
        highestSpendingCategory: d.fsa?.highestSpendingCategory ?? { name: "", amount: 0 },
        spendByCategory: d.fsa?.spendByCategory ?? [],
        monthlyIncomeVsExpenses: d.fsa?.monthlyIncomeVsExpenses ?? [],
        transactionCountByCategory: d.fsa?.transactionCountByCategory ?? [],
        dailySpendingTrend: d.fsa?.dailySpendingTrend ?? [],
        spendingByDayOfWeek: d.fsa?.spendingByDayOfWeek ?? [],
        top10LargestTransactions: d.fsa?.top10LargestTransactions ?? [],
        dateRangeText: d.fsa?.dateRangeText ?? "",
        summaryNotes: d.fsa?.summaryNotes ?? "",
      },

      categoryBreakdown: d.categoryBreakdown ?? empty.categoryBreakdown,

      health: normalizeHealthPayload(d.health, empty.health),
      monthlyFlow: normalizeMonthlyFlowPayload(d.monthlyFlow, empty.monthlyFlow),
      behaviour: d.behaviour ?? empty.behaviour,
      leakage: d.leakage ?? empty.leakage,
      filteredPie: d.filteredPie ?? empty.filteredPie,
      recipients: d.recipients ?? empty.recipients,
      anomaly: d.anomaly ?? empty.anomaly,
      balance: d.balance ?? empty.balance,
      recurring: d.recurring ?? empty.recurring,

      monthlyPredictionXai: d.monthlyPredictionXai ?? empty.monthlyPredictionXai,
      categoryPredictionXai: normalizeCategoryPredictionPayload(d.categoryPredictionXai, empty.categoryPredictionXai),
      aiRecommendations: d.aiRecommendations ?? empty.aiRecommendations,
    };
  } catch (err) {
    console.error("Failed to load dashboard data from backend:", err);
    throw err;
  }
}
import { getApiBaseUrl as getSharedApiBaseUrl } from "./api";
