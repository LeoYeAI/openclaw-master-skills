/**
 * OpenClaw FA Advisor Skill
 *
 * A comprehensive Financial Advisor skill for primary market financing
 */

// Export types
export * from './types/project.js';
export * from './types/investor.js';
export * from './types/models.js';

// Export modules
export { ProjectAssessor } from './modules/assessment/projectAssessor.js';
export { PitchDeckGenerator } from './modules/pitchdeck/deckGenerator.js';
export { ValuationEngine } from './modules/valuation/valuationEngine.js';
export { InvestorMatcher } from './modules/matching/investorMatcher.js';
export { InvestmentAnalyzer } from './modules/analysis/investmentAnalyzer.js';

// Main FA Advisor class
import type { Project } from './types/project.js';
import type { Investor } from './types/investor.js';
import { ProjectAssessor } from './modules/assessment/projectAssessor.js';
import { PitchDeckGenerator } from './modules/pitchdeck/deckGenerator.js';
import { ValuationEngine } from './modules/valuation/valuationEngine.js';
import { InvestorMatcher } from './modules/matching/investorMatcher.js';
import { InvestmentAnalyzer } from './modules/analysis/investmentAnalyzer.js';

/**
 * FA Advisor - Main class
 *
 * Provides comprehensive financial advisory services for:
 * - Startups seeking funding
 * - Investors evaluating opportunities
 */
export class FAAdvisor {
  private projectAssessor: ProjectAssessor;
  private pitchDeckGenerator: PitchDeckGenerator;
  private valuationEngine: ValuationEngine;
  private investorMatcher: InvestorMatcher;
  private investmentAnalyzer: InvestmentAnalyzer;

  constructor(investors: Investor[] = []) {
    this.projectAssessor = new ProjectAssessor();
    this.pitchDeckGenerator = new PitchDeckGenerator();
    this.valuationEngine = new ValuationEngine();
    this.investorMatcher = new InvestorMatcher(investors);
    this.investmentAnalyzer = new InvestmentAnalyzer();
  }

  /**
   * Complete startup package: assessment + deck + valuation + investor matching
   */
  async startupPackage(project: Project) {
    console.log('🚀 Generating complete startup fundraising package...\n');

    // 1. Project Assessment
    console.log('📊 Step 1/4: Assessing project...');
    const assessment = await this.projectAssessor.assess(project);
    console.log(`✅ Overall score: ${assessment.scores.overall}/100 - ${assessment.investmentReadiness}\n`);

    // 2. Pitch Deck & Business Plan
    console.log('📑 Step 2/4: Generating pitch deck and business plan...');
    const pitchDeck = await this.pitchDeckGenerator.generateOutline(project);
    const businessPlan = await this.pitchDeckGenerator.generateBusinessPlan(project);
    console.log(`✅ Generated ${pitchDeck.slides.length}-slide pitch deck\n`);

    // 3. Valuation Analysis
    console.log('💰 Step 3/4: Performing valuation analysis...');
    const valuation = await this.valuationEngine.comprehensiveValuation(project);
    console.log(`✅ Recommended pre-money valuation: $${this.formatNumber(valuation.recommendedValuation.preMoney)}\n`);

    // 4. Investor Matching
    console.log('🎯 Step 4/4: Matching with investors...');
    const investorMatches = await this.investorMatcher.matchInvestors(project, 20);
    const outreachStrategy = this.investorMatcher.generateOutreachStrategy(investorMatches);
    console.log(`✅ Found ${investorMatches.length} matching investors\n`);

    return {
      assessment,
      pitchDeck,
      businessPlan,
      valuation,
      investorMatches,
      outreachStrategy,
    };
  }

  /**
   * Investor package: analyze a deal from investor perspective
   */
  async investorPackage(project: Project) {
    console.log('🔍 Generating investment analysis package...\n');

    // 1. Investment Memo
    console.log('📝 Step 1/3: Generating investment memo...');
    const memo = await this.investmentAnalyzer.generateInvestmentMemo(project);
    const memoDocument = await this.investmentAnalyzer.generateMemoDocument(project);
    console.log(`✅ Investment recommendation: ${memo.recommendation.decision.toUpperCase()}\n`);

    // 2. Due Diligence Checklist
    console.log('✅ Step 2/3: Generating due diligence checklist...');
    const ddChecklist = this.investmentAnalyzer.generateDueDiligenceChecklist(project);
    console.log(`✅ Generated ${ddChecklist.length}-item DD checklist\n`);

    // 3. Valuation Analysis
    console.log('💰 Step 3/3: Performing valuation analysis...');
    const valuation = await this.valuationEngine.comprehensiveValuation(project);
    console.log(`✅ Fair valuation range: $${this.formatNumber(valuation.recommendedValuation.preMoney)}\n`);

    return {
      memo,
      memoDocument,
      ddChecklist,
      valuation,
    };
  }

  /**
   * Quick assessment - fast check of investment readiness
   */
  async quickAssessment(project: Project) {
    const assessment = await this.projectAssessor.assess(project);

    console.log(`\n📊 Quick Assessment: ${project.name}`);
    console.log(`${'='.repeat(50)}`);
    console.log(`Overall Score: ${assessment.scores.overall}/100`);
    console.log(`Investment Readiness: ${assessment.investmentReadiness.toUpperCase()}`);
    console.log(`\n🎯 Scores:`);
    console.log(`  Team:      ${assessment.scores.team}/100`);
    console.log(`  Market:    ${assessment.scores.market}/100`);
    console.log(`  Product:   ${assessment.scores.product}/100`);
    console.log(`  Traction:  ${assessment.scores.traction}/100`);
    console.log(`  Financials: ${assessment.scores.financials}/100`);

    console.log(`\n✅ Strengths:`);
    assessment.strengths.forEach(s => console.log(`  - ${s}`));

    console.log(`\n⚠️  Weaknesses:`);
    assessment.weaknesses.forEach(w => console.log(`  - ${w}`));

    console.log(`\n💡 Recommendations:`);
    assessment.recommendations.forEach(r => console.log(`  - ${r}`));

    return assessment;
  }

  /**
   * Generate pitch deck only
   */
  async generatePitchDeck(project: Project) {
    return await this.pitchDeckGenerator.generateOutline(project);
  }

  /**
   * Generate business plan only
   */
  async generateBusinessPlan(project: Project) {
    return await this.pitchDeckGenerator.generateBusinessPlan(project);
  }

  /**
   * Valuation analysis only
   */
  async valuate(project: Project) {
    return await this.valuationEngine.comprehensiveValuation(project);
  }

  /**
   * Match investors only
   */
  async matchInvestors(project: Project, topN: number = 20) {
    return await this.investorMatcher.matchInvestors(project, topN);
  }

  /**
   * Generate investment memo only
   */
  async analyzeForInvestor(project: Project) {
    return await this.investmentAnalyzer.generateInvestmentMemo(project);
  }

  // Helper
  private formatNumber(num: number): string {
    if (num >= 1_000_000_000) {
      return `${(num / 1_000_000_000).toFixed(1)}B`;
    } else if (num >= 1_000_000) {
      return `${(num / 1_000_000).toFixed(1)}M`;
    } else if (num >= 1_000) {
      return `${(num / 1_000).toFixed(1)}K`;
    }
    return num.toString();
  }
}

// Default export
export default FAAdvisor;
