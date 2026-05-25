import { z } from 'zod';
import { FundingStage, Industry, BusinessModel } from './project.js';

/**
 * 投资机构类型
 */
export enum InvestorType {
  VC = 'vc',
  PE = 'pe',
  CORPORATE_VC = 'corporate-vc',
  ANGEL = 'angel',
  FAMILY_OFFICE = 'family-office',
  ACCELERATOR = 'accelerator',
  GOVERNMENT = 'government',
}

/**
 * 投资地域偏好
 */
export enum GeographicFocus {
  NORTH_AMERICA = 'north-america',
  EUROPE = 'europe',
  ASIA = 'asia',
  CHINA = 'china',
  SOUTHEAST_ASIA = 'southeast-asia',
  LATIN_AMERICA = 'latin-america',
  MIDDLE_EAST = 'middle-east',
  AFRICA = 'africa',
  GLOBAL = 'global',
}

/**
 * 投资机构信息
 */
export const InvestorSchema = z.object({
  // 基本信息
  id: z.string(),
  name: z.string(),
  type: z.nativeEnum(InvestorType),
  website: z.string().url().optional(),
  description: z.string(),
  founded: z.number().optional(),
  headquarters: z.string(),

  // 基金信息
  fund: z.object({
    aum: z.number().optional(), // Assets Under Management
    currentFund: z.object({
      name: z.string(),
      size: z.number(),
      vintage: z.number(), // 年份
    }).optional(),
    fundHistory: z.array(z.object({
      name: z.string(),
      size: z.number(),
      vintage: z.number(),
    })).optional(),
  }).optional(),

  // 投资策略
  strategy: z.object({
    // 投资阶段
    stages: z.array(z.nativeEnum(FundingStage)),

    // 行业偏好
    industries: z.array(z.nativeEnum(Industry)),
    subIndustries: z.array(z.string()).optional(),

    // 商业模式偏好
    businessModels: z.array(z.nativeEnum(BusinessModel)).optional(),

    // 地域偏好
    geographicFocus: z.array(z.nativeEnum(GeographicFocus)),

    // 投资金额范围
    investmentRange: z.object({
      min: z.number(),
      max: z.number(),
      typical: z.number(),
    }),

    // 投资论点
    thesis: z.string().optional(),

    // 特殊关注领域
    specialFocus: z.array(z.string()).optional(),
  }),

  // 投资组合
  portfolio: z.object({
    totalInvestments: z.number(),
    activeInvestments: z.number(),
    exits: z.number(),
    notableCompanies: z.array(z.object({
      name: z.string(),
      industry: z.string(),
      outcome: z.enum(['active', 'ipo', 'acquired', 'failed']).optional(),
    })).optional(),
  }).optional(),

  // 团队
  team: z.array(z.object({
    name: z.string(),
    title: z.string(),
    linkedin: z.string().optional(),
    background: z.string().optional(),
  })).optional(),

  // 联系方式
  contact: z.object({
    email: z.string().email().optional(),
    phone: z.string().optional(),
    submissionUrl: z.string().url().optional(),
    preferredContact: z.enum(['email', 'submission-form', 'warm-intro', 'linkedin']).optional(),
  }).optional(),

  // 投资风格
  investmentStyle: z.object({
    leadInvestor: z.boolean(), // 是否做领投
    followOn: z.boolean(), // 是否跟投
    boardSeat: z.boolean(), // 是否要求董事会席位
    handsOn: z.enum(['very-hands-on', 'hands-on', 'moderate', 'hands-off']).optional(),
    valueAdd: z.array(z.string()).optional(), // 能提供的附加价值
  }).optional(),

  // 决策流程
  decisionProcess: z.object({
    averageTimeToDecision: z.number().optional(), // 天数
    decisionMakers: z.string().optional(),
    investmentCommitteeSchedule: z.string().optional(),
  }).optional(),

  // 元数据
  metadata: z.object({
    lastUpdated: z.string(),
    dataSource: z.array(z.string()).optional(),
    verifiedData: z.boolean().optional(),
  }),
});

export type Investor = z.infer<typeof InvestorSchema>;

/**
 * 投资人匹配结果
 */
export interface InvestorMatch {
  investor: Investor;
  matchScore: number; // 0-100
  matchReasons: string[];
  concerns: string[];
  approachStrategy: string;
  priority: 'high' | 'medium' | 'low';
}

/**
 * 投资分析备忘录
 */
export interface InvestmentMemo {
  project: {
    name: string;
    industry: string;
    stage: string;
  };
  executiveSummary: string;
  investmentHighlights: string[];
  marketOpportunity: {
    size: string;
    growth: string;
    dynamics: string;
  };
  competitivePosition: {
    strengths: string[];
    weaknesses: string[];
    differentiation: string;
  };
  teamAssessment: {
    overview: string;
    strengths: string[];
    gaps: string[];
  };
  financialAnalysis: {
    currentMetrics: Record<string, any>;
    projections: string;
    valuation: string;
  };
  risks: Array<{
    category: string;
    description: string;
    severity: 'low' | 'medium' | 'high';
    mitigation: string;
  }>;
  recommendation: {
    decision: 'pass' | 'maybe' | 'proceed' | 'strong-yes';
    reasoning: string;
    nextSteps: string[];
  };
}
