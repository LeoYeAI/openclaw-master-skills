# Python FA Advisor 快速开始

## 🚀 5分钟快速上手

### 1. 安装依赖

```bash
# 进入项目目录
cd /home/justin/ai-fa

# 安装 Python 包
pip install -e .

# 或使用 pip3
pip3 install -e .
```

### 2. 安装系统依赖（PDF 功能所需）

**macOS:**
```bash
brew install tesseract ghostscript poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils ghostscript
sudo apt-get install tesseract-ocr-chi-sim  # 中文支持
```

**Windows:**
- 下载并安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- 下载并安装 [Poppler](http://blog.alivate.com.au/poppler-windows/)

### 3. 验证安装

```bash
python3 -c "import fa_advisor; print('✅ FA Advisor installed successfully!')"
```

### 4. 运行示例

创建文件 `test_fa.py`:

```python
import asyncio
from fa_advisor import FAAdvisor, Project, FundingStage, Industry, BusinessModel
from fa_advisor.types.project import (
    Product, ProductStage, Market, Team, Founder,
    Financials, Revenue, Expenses, RevenueProjection,
    Fundraising, UseOfFunds
)

async def main():
    # 创建示例项目
    project = Project(
        name="CloudFlow AI",
        description="Enterprise AI workflow automation platform",
        location="Shanghai, China",
        industry=Industry.ENTERPRISE_SOFTWARE,
        business_model=BusinessModel.B2B_SAAS,
        target_market="Mid to large enterprises",

        product=Product(
            description="One-stop AI workflow platform",
            stage=ProductStage.LAUNCHED,
            key_features=[
                "Natural language workflow builder",
                "AI-driven optimization",
                "100+ enterprise integrations"
            ],
            unique_value_proposition="90% lower implementation cost vs traditional RPA",
            customer_pain_points=[
                "High RPA implementation cost",
                "Requires technical expertise",
                "Complex system integration"
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
                    name="Zhang Ming",
                    title="CEO & Co-founder",
                    background="Former Alibaba Senior Expert, 10 years enterprise software experience"
                ),
                Founder(
                    name="Li Hua",
                    title="CTO & Co-founder",
                    background="Former Huawei AI Lab Director, AI expert"
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
            )
        ),

        fundraising=Fundraising(
            current_stage=FundingStage.SERIES_A,
            target_amount=10_000_000,
            minimum_amount=8_000_000,
            use_of_funds=[
                UseOfFunds(category="R&D", percentage=40, description="Product development"),
                UseOfFunds(category="Sales & Marketing", percentage=35, description="Go to market"),
                UseOfFunds(category="Operations", percentage=15, description="General operations"),
                UseOfFunds(category="Reserve", percentage=10, description="Emergency buffer")
            ]
        )
    )

    # 初始化 FA Advisor
    advisor = FAAdvisor()

    # 快速评估
    print("\n" + "="*60)
    print("📊 QUICK ASSESSMENT")
    print("="*60)
    assessment = await advisor.quick_assessment(project)

    # 估值分析
    print("\n" + "="*60)
    print("💰 VALUATION ANALYSIS")
    print("="*60)
    valuation = await advisor.valuate(project)
    print(f"\n💵 Recommended Pre-Money: ${valuation.recommended_valuation.pre_money:,.0f}")
    print(f"💵 Post-Money: ${valuation.recommended_valuation.post_money:,.0f}")
    print(f"📝 Reasoning: {valuation.recommended_valuation.reasoning}")

    print("\n✅ FA Advisor Python版本运行成功！")

if __name__ == "__main__":
    asyncio.run(main())
```

运行：
```bash
python3 test_fa.py
```

### 5. PDF 处理示例

```python
import asyncio
from fa_advisor import FAAdvisor
from pathlib import Path

async def test_pdf():
    advisor = FAAdvisor()

    # 解析 PDF
    result = await advisor.parse_pdf("document.pdf")
    if result.success:
        print("Extracted text:", result.text[:500])
        print("Tables found:", len(result.tables) if result.tables else 0)

    # 解析财务报表
    financial_result = await advisor.parse_financial_pdf("financial_statement.pdf")
    if financial_result.success and financial_result.financial_data:
        data = financial_result.financial_data
        print(f"Revenue: ${data.revenue:,.0f}" if data.revenue else "N/A")
        print(f"Expenses: ${data.expenses:,.0f}" if data.expenses else "N/A")

    # OCR 扫描件
    ocr_result = await advisor.ocr_pdf("scanned.pdf")
    if ocr_result.success:
        print("OCR text:", ocr_result.text[:500])

asyncio.run(test_pdf())
```

## 📚 进一步学习

- 查看 `PYTHON_ARCHITECTURE.md` 了解完整架构
- 查看 `examples/` 目录中的更多示例
- 阅读 `pyproject.toml` 了解依赖配置

## 🐛 常见问题

### ImportError: No module named 'cv2'

```bash
pip install opencv-python
```

### Tesseract not found

确保 tesseract 已安装并在 PATH 中：
```bash
which tesseract  # macOS/Linux
where tesseract  # Windows
```

### Camelot table extraction fails

```bash
pip install "camelot-py[cv]"
pip install opencv-python
```

## 🎉 下一步

1. 完成其他业务模块的实现
2. 添加测试用例
3. 生成 PDF 报告
4. 更新 SKILL.md 为 Python 版本

需要帮助？查看 `PYTHON_ARCHITECTURE.md` 获取详细指南！
