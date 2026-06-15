#!/usr/bin/env python3
"""
FA Advisor Python 版本示例

这个脚本演示如何使用 Python 版本的 FA Advisor
"""

import asyncio
from fa_advisor import FAAdvisor, Project, FundingStage, Industry, BusinessModel
from fa_advisor.types.project import (
    Product, ProductStage, Market, Team, Founder,
    Financials, Revenue, Expenses, FinancialMetrics, RevenueProjection,
    Fundraising, UseOfFunds, Traction
)


async def main():
    print("\n" + "="*70)
    print("🐍 FA Advisor - Python 版本示例")
    print("="*70 + "\n")

    # 创建示例项目
    project = Project(
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
            competitors=[]
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
            awards=["36氪WISE 2023最具潜力企业"],
            press=["36氪", "TechCrunch"]
        )
    )

    # 初始化 FA Advisor
    advisor = FAAdvisor()

    print("✅ FA Advisor 初始化成功\n")

    # 1. 快速评估
    print("=" * 70)
    print("📊 测试 1: 快速评估")
    print("=" * 70)
    assessment = await advisor.quick_assessment(project)

    # 2. 估值分析
    print("\n" + "=" * 70)
    print("💰 测试 2: 估值分析")
    print("=" * 70)
    print("\n正在计算估值...")
    valuation = await advisor.valuate(project)

    print(f"\n💵 推荐的 Pre-Money 估值: ${valuation.recommended_valuation.pre_money:,.0f}")
    print(f"💵 Post-Money 估值: ${valuation.recommended_valuation.post_money:,.0f}")
    print(f"📝 估值依据: {valuation.recommended_valuation.reasoning}")

    print(f"\n📊 估值方法明细:")
    for method in valuation.valuation_by_method:
        print(f"  - {method.method}: ${method.valuation:,.0f} (置信度: {method.confidence})")

    # 3. Pitch Deck 生成
    print("\n" + "=" * 70)
    print("📑 测试 3: Pitch Deck 生成")
    print("=" * 70)
    print("\n正在生成 Pitch Deck...")
    pitch_deck = await advisor.generate_pitch_deck(project)

    print(f"\n✅ 已生成 {pitch_deck.total_slides} 页 Pitch Deck:")
    for slide in pitch_deck.slides:
        print(f"  Slide {slide.number}: {slide.title}")
        for point in slide.key_points[:2]:  # 只显示前2个要点
            print(f"    • {point}")

    # 4. PDF 处理能力演示（Python 核心优势）
    print("\n" + "=" * 70)
    print("📄 Python 独有优势: PDF 处理能力")
    print("=" * 70)
    print("""
Python 版本提供强大的 PDF 处理能力：

✅ 1. 财务报表解析
   - 自动提取收入、支出、利润等财务数据
   - 使用 camelot 精确提取PDF表格

   示例：
   result = await advisor.parse_financial_pdf("财务报表.pdf")
   print(f"营收: {result.financial_data.revenue}")

✅ 2. OCR 扫描件识别（支持中英文）
   - 使用 Tesseract OCR 引擎
   - 自动识别扫描版PDF中的文字

   示例：
   result = await advisor.ocr_pdf("扫描件.pdf", language='chi_sim+eng')

✅ 3. 专业 PDF 报告生成
   - 使用 ReportLab 生成专业投资报告
   - 自动排版、图表、样式

   示例：
   await advisor.pdf_generator.generate_assessment_report(
       assessment, "公司名称", "report.pdf"
   )

✅ 4. 表格数据分析
   - 提取的表格自动转为 Pandas DataFrame
   - 可以直接进行数据分析和可视化
""")

    # 总结
    print("\n" + "=" * 70)
    print("🎉 Python 版本测试完成！")
    print("=" * 70)
    print("""
✅ 已实现的功能：
  - 项目评估（完整实现）
  - 估值分析（简化实现，需完善）
  - Pitch Deck 生成（简化实现，需完善）
  - PDF 解析（完整实现）⭐
  - OCR 识别（完整实现）⭐
  - PDF 生成（完整实现）⭐

🔧 需要完善的功能：
  - 投资人匹配算法（参考 TypeScript 版本）
  - 投资分析模块（参考 TypeScript 版本）
  - 完整的估值模型（参考 TypeScript 版本）

📚 下一步：
  1. 查看 PYTHON_ARCHITECTURE.md 了解完整架构
  2. 查看 PYTHON_MIGRATION_SUMMARY.md 了解需要完成的工作
  3. 参考 TypeScript 版本实现剩余模块

💡 Python 版本的核心优势是 PDF 处理能力，这是 TypeScript 版本难以实现的！
""")


if __name__ == "__main__":
    asyncio.run(main())
