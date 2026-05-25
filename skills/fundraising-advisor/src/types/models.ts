/**
 * 估值方法
 */
export enum ValuationMethod {
  DCF = 'dcf', // Discounted Cash Flow
  COMPARABLE = 'comparable', // 可比公司法
  VENTURE_CAPITAL = 'venture-capital', // VC法
  SCORECARD = 'scorecard', // 记分卡法
  BERKUS = 'berkus', // Berkus法
  RISK_FACTOR = 'risk-factor', // 风险因素总和法
}

/**
 * 财务预测
 */
export interface FinancialProjection {
  year: number;
  revenue: number;
  cogs: number; // Cost of Goods Sold
  grossProfit: number;
  opex: {
    salesMarketing: number;
    researchDevelopment: number;
    generalAdministrative: number;
    total: number;
  };
  ebitda: number;
  netIncome: number;
  cashFlow: number;

  // 关键指标
  metrics: {
    revenueGrowth: number;
    grossMargin: number;
    operatingMargin: number;
    netMargin: number;
    burnRate: number;
  };
}

/**
 * 估值模型结果
 */
export interface ValuationResult {
  method: ValuationMethod;
  valuation: number;
  range: {
    low: number;
    mid: number;
    high: number;
  };
  assumptions: Array<{
    key: string;
    value: any;
    rationale: string;
  }>;
  multiples?: {
    revenueMultiple: number;
    ebitdaMultiple: number;
    userMultiple?: number;
  };
  sensitivityAnalysis?: Array<{
    variable: string;
    values: number[];
    valuations: number[];
  }>;
}

/**
 * 综合估值分析
 */
export interface ComprehensiveValuation {
  recommendedValuation: {
    preMoney: number;
    postMoney: number;
    methodology: string;
  };

  valuationByMethod: ValuationResult[];

  benchmarkData: {
    industryMedian: number;
    stageMedian: number;
    recentComparables: Array<{
      company: string;
      valuation: number;
      stage: string;
      date: string;
    }>;
  };

  dealTerms: {
    suggestedInvestment: number;
    suggestedEquity: number;
    suggestedValuation: number;
    liquidationPreference: string;
    antiDilution: string;
  };

  analysis: string;
  risks: string[];
}

/**
 * 融资结构
 */
export interface DealStructure {
  investment: {
    amount: number;
    currency: string;
  };

  valuation: {
    preMoney: number;
    postMoney: number;
    method: string;
  };

  equity: {
    newInvestorOwnership: number;
    founderOwnership: number;
    existingInvestorOwnership: number;
    optionPool: number;
  };

  terms: {
    liquidationPreference: {
      multiple: number;
      participating: boolean;
    };
    antiDilution: 'none' | 'weighted-average' | 'full-ratchet';
    boardSeats: {
      founders: number;
      investors: number;
      independent: number;
    };
    protectiveProvisions: string[];
    dragAlong: boolean;
    tagAlong: boolean;
    rightOfFirstRefusal: boolean;
  };

  milestones?: Array<{
    description: string;
    deadline: string;
    consequences: string;
  }>;
}
