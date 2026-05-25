import { z } from 'zod';

/**
 * 融资阶段
 */
export enum FundingStage {
  PRE_SEED = 'pre-seed',
  SEED = 'seed',
  SERIES_A = 'series-a',
  SERIES_B = 'series-b',
  SERIES_C = 'series-c',
  SERIES_D_PLUS = 'series-d-plus',
  PRE_IPO = 'pre-ipo'
}

/**
 * 行业分类
 */
export enum Industry {
  ENTERPRISE_SOFTWARE = 'enterprise-software',
  CONSUMER_INTERNET = 'consumer-internet',
  FINTECH = 'fintech',
  HEALTHCARE = 'healthcare',
  BIOTECH = 'biotech',
  AI_ML = 'ai-ml',
  ECOMMERCE = 'ecommerce',
  HARDWARE = 'hardware',
  BLOCKCHAIN = 'blockchain',
  EDTECH = 'edtech',
  CLEANTECH = 'cleantech',
  LOGISTICS = 'logistics',
  OTHER = 'other'
}

/**
 * 商业模式
 */
export enum BusinessModel {
  B2B_SAAS = 'b2b-saas',
  B2C = 'b2c',
  MARKETPLACE = 'marketplace',
  PLATFORM = 'platform',
  TRANSACTION = 'transaction',
  SUBSCRIPTION = 'subscription',
  FREEMIUM = 'freemium',
  ENTERPRISE = 'enterprise',
  HYBRID = 'hybrid'
}

/**
 * 创业项目基本信息
 */
export const ProjectSchema = z.object({
  // 基本信息
  name: z.string(),
  tagline: z.string().optional(),
  description: z.string(),
  foundedDate: z.string().optional(),
  location: z.string(),
  website: z.string().url().optional(),

  // 业务信息
  industry: z.nativeEnum(Industry),
  subIndustry: z.string().optional(),
  businessModel: z.nativeEnum(BusinessModel),
  targetMarket: z.string(),

  // 产品信息
  product: z.object({
    description: z.string(),
    stage: z.enum(['idea', 'prototype', 'mvp', 'launched', 'scaling']),
    keyFeatures: z.array(z.string()),
    uniqueValueProposition: z.string(),
    customerPainPoints: z.array(z.string()),
  }),

  // 市场信息
  market: z.object({
    tam: z.number().optional(), // Total Addressable Market
    sam: z.number().optional(), // Serviceable Addressable Market
    som: z.number().optional(), // Serviceable Obtainable Market
    marketGrowthRate: z.number().optional(),
    competitors: z.array(z.object({
      name: z.string(),
      description: z.string().optional(),
      differentiation: z.string().optional(),
    })),
  }),

  // 团队信息
  team: z.object({
    founders: z.array(z.object({
      name: z.string(),
      title: z.string(),
      background: z.string(),
      linkedin: z.string().optional(),
    })),
    teamSize: z.number(),
    keyHires: z.array(z.string()).optional(),
  }),

  // 财务信息
  financials: z.object({
    revenue: z.object({
      current: z.number(),
      projected: z.array(z.object({
        year: z.number(),
        amount: z.number(),
      })),
    }).optional(),
    expenses: z.object({
      monthly: z.number(),
      runway: z.number(), // 跑道（月）
    }).optional(),
    metrics: z.object({
      arr: z.number().optional(), // Annual Recurring Revenue
      mrr: z.number().optional(), // Monthly Recurring Revenue
      grossMargin: z.number().optional(),
      customerAcquisitionCost: z.number().optional(),
      lifetimeValue: z.number().optional(),
      churnRate: z.number().optional(),
    }).optional(),
  }),

  // 融资信息
  fundraising: z.object({
    currentStage: z.nativeEnum(FundingStage),
    targetAmount: z.number(),
    minimumAmount: z.number().optional(),
    currentValuation: z.number().optional(),
    previousRounds: z.array(z.object({
      stage: z.nativeEnum(FundingStage),
      amount: z.number(),
      date: z.string(),
      investors: z.array(z.string()),
      valuation: z.number().optional(),
    })).optional(),
    useOfFunds: z.array(z.object({
      category: z.string(),
      percentage: z.number(),
      description: z.string(),
    })),
  }),

  // 牵引力/成就
  traction: z.object({
    customers: z.number().optional(),
    users: z.number().optional(),
    growth: z.string().optional(),
    partnerships: z.array(z.string()).optional(),
    awards: z.array(z.string()).optional(),
    press: z.array(z.string()).optional(),
  }).optional(),
});

export type Project = z.infer<typeof ProjectSchema>;

/**
 * 项目评估结果
 */
export interface ProjectAssessment {
  project: Project;
  scores: {
    overall: number; // 0-100
    team: number;
    market: number;
    product: number;
    traction: number;
    financials: number;
  };
  strengths: string[];
  weaknesses: string[];
  risks: Array<{
    category: string;
    description: string;
    severity: 'low' | 'medium' | 'high';
    mitigation: string;
  }>;
  recommendations: string[];
  investmentReadiness: 'not-ready' | 'needs-work' | 'ready' | 'highly-ready';
}

/**
 * Pitch Deck 大纲
 */
export interface PitchDeckOutline {
  slides: Array<{
    number: number;
    title: string;
    type: 'cover' | 'problem' | 'solution' | 'market' | 'product' | 'business-model' |
           'traction' | 'competition' | 'team' | 'financials' | 'ask' | 'vision';
    keyPoints: string[];
    notes: string;
  }>;
}
