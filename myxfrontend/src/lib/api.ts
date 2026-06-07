// API service for backend integration
import { getAccessToken } from "./auth";

export function getApiBaseUrl() {
  const url =
    import.meta.env.VITE_API_URL ??
    import.meta.env.VITE_API_BASE_URL ??
    "https://tranzact-ai.onrender.com";

  console.log("API URL:", url);

  return url.replace(/\/+$/, "");
}
const API_BASE_URL = getApiBaseUrl();

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// Spending Analysis API Types
export interface CategoryAmount {
  category: string;
  amount: number;
}

export interface Transaction {
  amount: number;
  desc: string;
  date: string;
}

export interface MonthAmount {
  month: string;
  amount: number;
}

export interface SizeDistribution {
  bucket: "Micro" | "Small" | "Medium" | "Large" | "Very Large";
  range: string;
  count: number;
  total: number;
}

export interface CategoryConsistency {
  category: string;
  consistencyPct: number;
}

export interface BehaviourData {
  weekendTotal: number;
  weekdayTotal: number;
  weekendAvg: number;
  weekdayAvg: number;
  mostExpensiveMonth: MonthAmount;
  cheapestMonth: MonthAmount;
  avgMonthlySpend: number;
  stdDeviation: number;
  sizeDistribution: SizeDistribution[];
  categoryConsistency: CategoryConsistency[];
}

export interface SpendingAnalysisResponse {
  spendByCategory: CategoryAmount[];
  top10LargestTransactions: Transaction[];
  behaviour: BehaviourData;
}

// Prediction API Types
export interface ShapFactor {
  label: string;
  value: number;
}

export interface ShapWaterfallItem {
  label: string;
  value: number;
  direction: "up" | "down";
}

export interface SpendingDnaItem {
  label: string;
  importance: number;
}

export interface PredictionBottomLine {
  driverLabel: string;
  sizeWord: string;
  impactAmount: number;
  impactDirection: "up" | "down";
  pressurePct: number;
  pressureLabel: string;
  plainEnglishLines: string[];
}

export interface MonthlyPredictionResponse {
  predictMonthLabel: string;
  startingBaseline: number;
  aiForecast: number;
  actualSpend: number | null;
  forecastError: number;
  lastKnownMonth: string;
  forecastAmount: number;
  baselineAmount: number;
  topUpFactors: ShapFactor[];
  topDownFactors: ShapFactor[];
  bottomLine: PredictionBottomLine;
  shapWaterfall: ShapWaterfallItem[];
  spendingDna: SpendingDnaItem[];
}

export interface CategoryPredictionItem {
  predictMonthLabel: string;
  categoryName: string;
  predictedSpend: number;
  startingBaseline: number;
  aiForecast: number;
  actualSpend: number | null;
  forecastError: number;
  lastKnownMonth: string;
  topUpFactors: ShapFactor[];
  topDownFactors: ShapFactor[];
  bottomLine: PredictionBottomLine;
  shapWaterfall: ShapWaterfallItem[];
}

export interface CategoryPredictionResponse {
  categories: CategoryPredictionItem[];
}

// Recommendation API Types
export interface RecommendationCard {
  id: string;
  number: number;
  text: string;
}

export interface RecommendationResponse {
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
  cards: RecommendationCard[];
}

// Preprocessing API Types
export interface SupportedBank {
  name: string;
  formats: string[];
}

export interface PreprocessingResponse {
  message: string;
  user_name: string;
  statement_user_name?: string | null;
  bank_name: string;
  file_path: string;
  row_count: number;
  date_range: string;
  categories: string[];
}

export interface UploadHistoryItem {
  filename: string;
  display_name: string;
  bank_name: string;
  uploaded_at: string;
  uploaded_date: string;
  uploaded_time: string;
  is_current: boolean;
}

export interface UploadHistoryResponse {
  uploads: UploadHistoryItem[];
}

export interface AuthUser {
  id: number;
  email: string;
  first_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface DashboardOverviewCard {
  label: string;
  amount: number;
  changePct: number;
}

export interface DashboardOverviewFlowPoint {
  month: string;
  income: number;
  expenses: number;
}

export interface DashboardOverviewCategoryPoint {
  category: string;
  amount: number;
}

export interface DashboardOverviewTransaction {
  description: string;
  category: string;
  date: string;
  amount: number;
}

export interface DashboardOverviewHighlight {
  amount: number;
  description: string;
  date: string;
}

export interface FilteredPieChartSlice {
  category: string;
  amount: number;
}

export interface FilteredPieChartComparison {
  category: string;
  current: number;
  previous: number;
}

export interface FilteredPieChartResponse {
  availableMonths: string[];
  availableWeeks: string[];
  categoryBreakdown: FilteredPieChartSlice[];
  comparisonBreakdown: FilteredPieChartComparison[];
  comparisonPeriodLabel?: string;
  monthlyPieGrid: { month: string; slices: FilteredPieChartSlice[] }[];
}

export interface DashboardOverviewResponse {
  summaryCards: DashboardOverviewCard[];
  monthlyFinancialFlow: DashboardOverviewFlowPoint[];
  spendingByCategory: DashboardOverviewCategoryPoint[];
  transactionHistory: DashboardOverviewTransaction[];
  spendingHighlights: {
    highestSingleSpend: DashboardOverviewHighlight;
    lowestSingleSpend: DashboardOverviewHighlight;
  };
}

// API Client
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const accessToken = getAccessToken();
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  async register(payload: { email: string; first_name: string; password: string }): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async login(payload: { email: string; password: string }): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getCurrentUser(): Promise<AuthUser> {
    return this.request<AuthUser>('/api/auth/me');
  }

  async getDashboard(userName: string) {
    return this.request(`/api/dashboard?user_name=${encodeURIComponent(userName)}`);
  }

  async getDashboardOverview(userName: string): Promise<DashboardOverviewResponse> {
    return this.request<DashboardOverviewResponse>(`/api/dashboard-overview?user_name=${encodeURIComponent(userName)}`);
  }

  // Spending Analysis Endpoints
  async getFullSpendingAnalysis(userName: string): Promise<SpendingAnalysisResponse> {
    return this.request<SpendingAnalysisResponse>(`/full-spending-analysis/${encodeURIComponent(userName)}`);
  }

  async getSpendingAnalysis(userName: string): Promise<SpendingAnalysisResponse> {
    return this.request<SpendingAnalysisResponse>(`/full-spending-analysis/${encodeURIComponent(userName)}`);
  }

  async getCategoryBreakdown(userName: string) {
    return this.request(`/full-spending-analysis/${encodeURIComponent(userName)}/categories`);
  }

  async getSpendingTrends(userName: string, period: 'monthly' | 'weekly' | 'daily' = 'monthly') {
    return this.request(`/full-spending-analysis/${encodeURIComponent(userName)}/trends?period=${period}`);
  }

  async getLeakageAnalysis(userName: string) {
    return this.request(`/full-spending-analysis/${encodeURIComponent(userName)}/leakage`);
  }

  async getDetailedCategoryBreakdown(userName: string) {
    return this.request(`/api/analysis/category-breakdown?user_name=${encodeURIComponent(userName)}`);
  }

  async getFinancialHealthSummary(userName: string) {
    return this.request(`/api/analysis/health-summary?user_name=${encodeURIComponent(userName)}`);
  }

  async getMonthlyFlowAnalysis(userName: string) {
    return this.request(`/api/analysis/monthly-flow?user_name=${encodeURIComponent(userName)}`);
  }

  async getBehaviourPatterns(userName: string) {
    return this.request(`/api/analysis/behaviour-patterns?user_name=${encodeURIComponent(userName)}`);
  }

  async getFinancialLeakageSummary(userName: string) {
    return this.request(`/api/analysis/financial-leakage?user_name=${encodeURIComponent(userName)}`);
  }

  async getFilteredPieChart(userName: string, filterBy = "month", periodValue = "all"): Promise<FilteredPieChartResponse> {
    return this.request<FilteredPieChartResponse>(
      `/api/analysis/pie-chart?user_name=${encodeURIComponent(userName)}&filter_by=${encodeURIComponent(filterBy)}&period_value=${encodeURIComponent(periodValue)}`,
    );
  }

  async getTransfersOut(userName: string, filterBy = "month", periodValue = "all", topN = 10) {
    return this.request(
      `/api/analysis/transfers-out?user_name=${encodeURIComponent(userName)}&filter_by=${encodeURIComponent(filterBy)}&period_value=${encodeURIComponent(periodValue)}&top_n=${topN}`,
    );
  }

  async getAnomalies(userName: string) {
    return this.request(`/api/analysis/anomalies?user_name=${encodeURIComponent(userName)}`);
  }

  async getBalanceTrajectory(userName: string) {
    return this.request(`/api/analysis/balance-trajectory?user_name=${encodeURIComponent(userName)}`);
  }

  async getRecurringTransactions(userName: string) {
    return this.request(`/api/analysis/recurring?user_name=${encodeURIComponent(userName)}`);
  }

  // Prediction Endpoints
  async getMonthlyPrediction(userName: string, predictYear: number, predictMonthNum: number): Promise<MonthlyPredictionResponse> {
    return this.request<MonthlyPredictionResponse>('/api/predict/monthly', {
      method: 'POST',
      body: JSON.stringify({ user_name: userName, predict_year: predictYear, predict_month_num: predictMonthNum }),
    });
  }

  async getCategoryPrediction(userName: string, predictYear: number, predictMonthNum: number): Promise<CategoryPredictionResponse> {
    return this.request<CategoryPredictionResponse>('/api/predict/category', {
      method: 'POST',
      body: JSON.stringify({ user_name: userName, predict_month: "", predict_month_num: predictMonthNum, predict_year: predictYear }),
    });
  }

  // Recommendation Endpoint
  async getRecommendations(userName: string): Promise<RecommendationResponse> {
    return this.request<RecommendationResponse>('/api/recommend', {
      method: 'POST',
      body: JSON.stringify({ user_name: userName }),
    });
  }

  // Preprocessing Endpoints
  async uploadBankStatement(file: File, userName: string, bankName: string): Promise<PreprocessingResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_name', userName);
    formData.append('bank_name', bankName);

    const url = `${this.baseUrl}/api/preprocess/upload`;
    const accessToken = getAccessToken();
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      headers: {
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  async getSupportedBanks(): Promise<{ banks: SupportedBank[] }> {
    return this.request<{ banks: SupportedBank[] }>('/api/preprocess/supported-banks');
  }

  async getUploadHistory(userName: string): Promise<UploadHistoryResponse> {
    return this.request<UploadHistoryResponse>(`/api/preprocess/uploads?user_name=${encodeURIComponent(userName)}`);
  }

  async selectUpload(userName: string, filename: string): Promise<PreprocessingResponse> {
    return this.request<PreprocessingResponse>('/api/preprocess/uploads/select', {
      method: 'POST',
      body: JSON.stringify({ user_name: userName, filename }),
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request('/health');
  }
}

export const api = new ApiClient();

// React Query hooks (if using TanStack Query)
export const useSpendingAnalysis = (userName: string) => {
  return {
    queryKey: ['spending-analysis', userName],
    queryFn: () => api.getSpendingAnalysis(userName),
    staleTime: 5 * 60 * 1000, // 5 minutes
  };
};

export const useCategoryBreakdown = (userName: string) => {
  return {
    queryKey: ['category-breakdown', userName],
    queryFn: () => api.getCategoryBreakdown(userName),
    staleTime: 5 * 60 * 1000,
  };
};

export const useSpendingTrends = (userName: string, period: 'monthly' | 'weekly' | 'daily' = 'monthly') => {
  return {
    queryKey: ['spending-trends', userName, period],
    queryFn: () => api.getSpendingTrends(userName, period),
    staleTime: 5 * 60 * 1000,
  };
};

export const useLeakageAnalysis = (userName: string) => {
  return {
    queryKey: ['leakage-analysis', userName],
    queryFn: () => api.getLeakageAnalysis(userName),
    staleTime: 5 * 60 * 1000,
  };
};
