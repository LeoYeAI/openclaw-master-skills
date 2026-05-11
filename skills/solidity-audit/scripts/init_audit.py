#!/usr/bin/env python3
"""
Solidity审计项目初始化脚本
创建标准化的审计项目目录结构
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

AUDIT_STRUCTURE = """
audit-{project_name}/
├── contracts/          # 待审计合约
│   └── src/
├── analysis/           # 分析结果
│   ├── slither/
│   ├── aderyn/
│   └── manual/
├── test/               # 测试文件
│   └── poc/
├── reports/            # 审计报告
│   └── drafts/
├── notes/              # 审计笔记
├── findings.json       # 发现汇总
└── README.md           # 项目说明
"""

README_TEMPLATE = """# {project_name} 审计项目

**审计时间**: {date}
**目标安全等级**: [S] 基础级 / [M] 中级 / [Q] 高级

## 审计进度

- [ ] 项目准备
- [ ] 自动化扫描
- [ ] 人工核查
- [ ] 测试验证
- [ ] 报告撰写

## 合约列表

| 合约 | 行数 | 功能 | 状态 |
|------|------|------|------|
| - | - | - | 待审计 |

## 发现汇总

| 编号 | 严重程度 | 描述 | 状态 |
|------|----------|------|------|
| - | - | - | - |

## 工具命令

```bash
# Slither扫描
slither contracts/src --exclude-dependencies --json analysis/slither/results.json

# Aderyn扫描
aderyn contracts/src -o analysis/aderyn/report.md

# Foundry测试
forge test -vvv --fuzz-runs 10000
```

## 参考资料

- [EEA EthTrust V3](https://entethalliance.org/specs/ethtrust-sl/v3/)
- [项目文档链接]
"""

FINDINGS_TEMPLATE = """{
  "project": "{project_name}",
  "date": "{date}",
  "target_level": "M",
  "findings": [
    {
      "id": "H-01",
      "severity": "High",
      "title": "示例发现",
      "status": "Open",
      "contract": "",
      "line": 0,
      "description": "",
      "impact": "",
      "recommendation": "",
      "eea_requirement": ""
    }
  ],
  "eea_compliance": {
    "S": {"passed": 0, "failed": 0, "na": 0},
    "M": {"passed": 0, "failed": 0, "na": 0},
    "Q": {"passed": 0, "failed": 0, "na": 0}
  }
}
"""

def create_audit_project(project_name: str, output_dir: str = "."):
    """创建审计项目目录结构"""
    
    base_path = Path(output_dir) / f"audit-{project_name}"
    
    if base_path.exists():
        print(f"错误: 目录 {base_path} 已存在")
        return False
    
    # 创建目录结构
    directories = [
        "contracts/src",
        "analysis/slither",
        "analysis/aderyn",
        "analysis/manual",
        "test/poc",
        "reports/drafts",
        "notes"
    ]
    
    for dir_path in directories:
        (base_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # 创建README
    readme_content = README_TEMPLATE.format(
        project_name=project_name,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    (base_path / "README.md").write_text(readme_content)
    
    # 创建findings.json
    findings_content = FINDINGS_TEMPLATE.format(
        project_name=project_name,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    (base_path / "findings.json").write_text(findings_content)
    
    print(f"✅ 审计项目已创建: {base_path}")
    print("\n目录结构:")
    print(AUDIT_STRUCTURE.format(project_name=project_name))
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="初始化Solidity审计项目"
    )
    parser.add_argument(
        "project_name",
        help="项目名称（将创建 audit-{name} 目录）"
    )
    parser.add_argument(
        "-o", "--output",
        default=".",
        help="输出目录（默认当前目录）"
    )
    
    args = parser.parse_args()
    
    create_audit_project(args.project_name, args.output)


if __name__ == "__main__":
    main()