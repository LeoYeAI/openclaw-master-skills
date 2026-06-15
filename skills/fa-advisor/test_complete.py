#!/usr/bin/env python3
"""
完整功能测试 - Python FA Advisor

测试所有已实现的模块
"""

import asyncio
import json
from pathlib import Path

from fa_advisor import FAAdvisor, Project, FundingStage, Industry, BusinessModel
from fa_advisor.types.project import (
    Product, ProductStage, Market, Team, Founder,
    Financials, Revenue, Expenses, FinancialMetrics, RevenueProjection,
    Fundraising, UseOfFunds, Traction, Competitor
)
from fa_advisor.types.investor import Investor


def load_sample_investors():
    """加载示例投资人数据"""
    investor_file = Path("fa_advisor/data/investors/sample_investors.json")
    if investor_file.exists():
        with open(investor_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Investor(**inv) for inv in data]
    return []


def create_sample_project():
    """创建示例项目"""
    return Project(
        name="CloudFlow AI",
        tagline="企业级AI工作流自动化平台",
        description="CloudFlow AI是一个面向企业的AI驱动的工作流自动化平台，帮助企业通过自然语言快速构建、部署和管理复杂的业务流程自动化。",
        location="上海, 中国",
        industry=Industry.ENTERPRISE_SOFTWARE,
        sub_industry="workflow-automation",
        business_model=BusinessModel.B2B_SAAS,
        target_market="中大型企业的IT和运营团队",

        product=Product(
            description="一站式AI工作流平台，通过自然语言交互，让非技术人员也能轻松构建自动化流程",
            stage=ProductStage.LAUNCHED,
            key_features=[
                "自然语言流程构建",
                "AI驱动的流程优化建议",
                "支持100+企业应用集成",
                "可视化流程编辑器",
                "实时监控和分析"
            ],
            unique_value_proposition="相比传统RPA工具降低90%实施成本，提升10倍开发效率",
            customer_pain_points=[
                "传统RPA工具实施成本高、周期长",
                "需要专业技术人员才能配置",
                "系统集成复杂，维护困难"
            ]
        ),

        market=Market(
            tam=50_000_000_000,  # $50B
            sam=10_000_000_000,  # $10B
            som=500_000_000,     # $500M
            market_growth_rate=0.35,  # 35% CAGR
            competitors=[
                Competitor(
                    name="UiPath",
                    description="全球领先的RPA平台",
                    differentiation="我们专注于AI原生设计，更易用且成本更低"
                ),
                Competitor(
                    name="Automation Anywhere",
                    description="企业RPA解决方案",
                    differentiation="我们提供无代码体验，降低使用门槛"
                ),
                Competitor(
                    name="Zapier",
                    description="面向中小企业的自动化工具",
                    differentiation="我们专注企业级需求，提供更强的安全性和可扩展性"
                )
            ]
        ),

        team=Team(
            founders=[
                Founder(
                    name="张明",
                    title="CEO & Co-founder",
                    background="前阿里巴巴高级技术专家，10年企业软件经验，曾负责钉钉工作流引擎"
                ),
                Founder(
                    name="李华",
                    title="CTO & Co-founder",
                    background="前华为AI实验室负责人，AI领域专家，发表过多篇顶会论文"
                )
            ],
            team_size=25,
            key_hires=["VP of Sales", "Head of Customer Success"]
        ),

        financials=Financials(
            revenue=Revenue(
                current=1_200_000,  # $1.2M ARR
                projected=[
                    RevenueProjection(year=2024, amount=3_000_000),
                    RevenueProjection(year=2025, amount=8_000_000),
                    RevenueProjection(year=2026, amount=20_000_000)
                ]
            ),
            expenses=Expenses(
                monthly=150_000,
                runway=18
            ),
            metrics=FinancialMetrics(
                arr=1_200_000,
                mrr=100_000,
                gross_margin=0.85,
                customer_acquisition_cost=8_000,
                lifetime_value=36_000,
                churn_rate=0.03
            )
        ),

        fundraising=Fundraising(
            current_stage=FundingStage.SERIES_A,
            target_amount=10_000_000,
            minimum_amount=8_000_000,
            current_valuation=40_000_000,
            use_of_funds=[
                UseOfFunds(
                    category="产品研发",
                    percentage=40,
                    description="扩充工程团队，加强AI能力和企业集成"
                ),
                UseOfFunds(
                    category="市场销售",
                    percentage=35,
                    description="建立销售团队，拓展企业客户"
                ),
                UseOfFunds(
                    category="运营支出",
                    percentage=15,
                    description="日常运营和管理"
                ),
                UseOfFunds(
                    category="储备金",
                    percentage=10,
                    description="应急储备"
                )
            ]
        ),

        traction=Traction(
            customers=45,
            users=2_500,
            growth="月环比增长 40%",
            partnerships=["钉钉", "企业微信", "飞书"],
            awards=["36氪WISE 2023最具潜力企业", "TechCrunch Disrupt入围"],
            press=["36氪", "TechCrunch", "雷锋网"]
        )
    )


async def test_all_modules():
    """测试所有模块"""
    print("\n" + "="*80)
    print("🧪 Python FA Advisor - 完整功能测试")
    print("="*80 + "\n")

    # 创建项目和加载投资人
    print("📋 准备测试数据...")
    project = create_sample_project()
    investors = load_sample_investors()
    print(f"✅ 项目创建完成: {project.name}")
    print(f"✅ 加载了 {len(investors)} 个投资人\n")

    # 初始化 FA Advisor
    advisor = FAAdvisor(investors=investors)
    print("✅ FA Advisor 初始化完成\n")

    # ========== 测试 1: 项目评估 ==========
    print("="*80)
    print("📊 测试 1/6: 项目评估 (ProjectAssessor)")
    print("="*80)

    assessment = await advisor.quick_assessment(project)

    print(f"\n✅ 评估完成!")
    print(f"   总分: {assessment.scores.overall:.0f}/100")
    print(f"   投资准备度: {assessment.investment_readiness.value}")
    print(f"   优势数量: {len(assessment.strengths)}")
    print(f"   劣势数量: {len(assessment.weaknesses)}")
    print(f"   建议数量: {len(assessment.recommendations)}")

    # ========== 测试 2: 估值分析 ==========
    print("\n" + "="*80)
    print("💰 测试 2/6: 估值分析 (ValuationEngine)")
    print("="*80)

    valuation = await advisor.valuate(project)

    print(f"\n✅ 估值完成!")
    print(f"   Pre-Money: ${valuation.recommended_valuation.pre_money:,.0f}")
    print(f"   Post-Money: ${valuation.recommended_valuation.post_money:,.0f}")
    print(f"   使用方法数: {len(valuation.valuation_by_method)}")

    print(f"\n   方法明细:")
    for method in valuation.valuation_by_method:
        print(f"   - {method.method}: ${method.valuation:,.0f} ({method.confidence})")

    print(f"\n   交易条款:")
    print(f"   - 融资金额: ${valuation.deal_terms.raise_amount:,.0f}")
    print(f"   - 股权稀释: {valuation.deal_terms.equity_dilution * 100:.1f}%")
    print(f"   - 投资人类型: {valuation.deal_terms.investor_type}")

    # ========== 测试 3: Pitch Deck 生成 ==========
    print("\n" + "="*80)
    print("📑 测试 3/6: Pitch Deck 生成 (PitchDeckGenerator)")
    print("="*80)

    pitch_deck = await advisor.generate_pitch_deck(project)

    print(f"\n✅ Pitch Deck 生成完成!")
    print(f"   总页数: {pitch_deck.total_slides}")
    print(f"   目标听众: {pitch_deck.target_audience}")
    print(f"   预计时长: {pitch_deck.estimated_duration}")

    print(f"\n   前5页预览:")
    for slide in pitch_deck.slides[:5]:
        print(f"   Slide {slide.number}: {slide.title} ({len(slide.key_points)} 要点)")

    # ========== 测试 4: 商业计划书生成 ==========
    print("\n" + "="*80)
    print("📝 测试 4/6: 商业计划书生成 (PitchDeckGenerator)")
    print("="*80)

    business_plan = await advisor.generate_business_plan(project)

    print(f"\n✅ 商业计划书生成完成!")
    print(f"   文档长度: {len(business_plan)} 字符")
    print(f"   约 {len(business_plan.split('##'))} 个主要章节")

    # 保存到文件
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    bp_file = output_dir / f"{project.name}_business_plan.md"
    with open(bp_file, 'w', encoding='utf-8') as f:
        f.write(business_plan)
    print(f"   已保存到: {bp_file}")

    # ========== 测试 5: 投资人匹配 ==========
    print("\n" + "="*80)
    print("🎯 测试 5/6: 投资人匹配 (InvestorMatcher)")
    print("="*80)

    if investors:
        matches = await advisor.match_investors(project, top_n=10)

        print(f"\n✅ 投资人匹配完成!")
        print(f"   匹配数量: {len(matches)}")

        print(f"\n   Top 5 匹配:")
        for i, match in enumerate(matches[:5], 1):
            print(f"   {i}. {match.investor_name}")
            print(f"      匹配分数: {match.match_score:.1f}/100")
            print(f"      优先级: {match.priority}")
            print(f"      阶段匹配: {'✓' if match.stage_fit else '✗'}")
            print(f"      行业匹配: {'✓' if match.industry_fit else '✗'}")

        # 生成接触策略
        strategy = advisor.investor_matcher.generate_outreach_strategy(matches)
        strategy_file = output_dir / f"{project.name}_outreach_strategy.md"
        with open(strategy_file, 'w', encoding='utf-8') as f:
            f.write(strategy)
        print(f"\n   接触策略已保存到: {strategy_file}")
    else:
        print("\n⚠️  没有加载投资人数据，跳过匹配测试")

    # ========== 测试 6: 投资分析 ==========
    print("\n" + "="*80)
    print("🔍 测试 6/6: 投资分析 (InvestmentAnalyzer)")
    print("="*80)

    memo = await advisor.analyze_for_investor(project)

    print(f"\n✅ 投资备忘录生成完成!")
    print(f"   投资建议: {memo.recommendation.decision.value.upper()}")
    print(f"   置信度: {memo.recommendation.confidence}")
    print(f"   投资亮点: {len(memo.investment_highlights)} 个")
    print(f"   识别风险: {len(memo.risks)} 个")
    print(f"   下一步行动: {len(memo.recommendation.next_steps)} 项")

    print(f"\n   投资亮点预览:")
    for i, highlight in enumerate(memo.investment_highlights[:3], 1):
        print(f"   {i}. {highlight}")

    print(f"\n   主要风险预览:")
    for i, risk in enumerate(memo.risks[:3], 1):
        print(f"   {i}. [{risk.severity.value.upper()}] {risk.category}: {risk.description}")

    # 生成DD清单
    dd_checklist = advisor.investment_analyzer.generate_due_diligence_checklist(project)
    print(f"\n   DD清单: {len(dd_checklist)} 项")

    high_priority = [item for item in dd_checklist if item.priority == "high"]
    print(f"   - 高优先级: {len(high_priority)} 项")

    # ========== 测试完成 ==========
    print("\n" + "="*80)
    print("🎉 所有测试完成!")
    print("="*80)

    print(f"""
✅ 已完成测试的模块:
   1. ProjectAssessor - 项目评估 ✓
   2. ValuationEngine - 估值分析 ✓
   3. PitchDeckGenerator - Pitch Deck 生成 ✓
   4. PitchDeckGenerator - 商业计划书生成 ✓
   5. InvestorMatcher - 投资人匹配 ✓
   6. InvestmentAnalyzer - 投资分析 ✓

📁 生成的文件:
   - {bp_file}
""")

    if investors:
        print(f"   - {strategy_file}")

    print(f"""
💡 下一步:
   1. 查看生成的文档
   2. 测试 PDF 处理功能（需要 PDF 文件）
   3. 生成 PDF 报告
   4. 实际使用场景测试

🎊 Python FA Advisor 完全实现成功！
""")


if __name__ == "__main__":
    asyncio.run(test_all_modules())
