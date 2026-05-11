#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证脚本 - 校验 data.json 的字段命名和数据一致性

使用方式:
    python scripts/validate_data.py path/to/data.json

验证项:
    1. 字段命名规范（禁止模糊的命名如 top3_concentration）
    2. 数据一致性（数值在合理范围内）
    3. 必填字段完整性
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any


class DataValidator:
    """数据验证器"""

    # 禁止的模糊字段名
    FORBIDDEN_FIELDS = {
        'top3_concentration': '请使用 top3_product_concentration 或 top3_brand_concentration',
        'top10_concentration': '请使用 top10_product_concentration 或 top10_brand_concentration',
        'concentration': '请明确指定是产品还是品牌的集中度',
    }

    # 必填字段
    REQUIRED_FIELDS = {
        'metadata': ['category', 'site', 'date'],
        'market_overview': [
            'top100_monthly_sales',
            'top100_monthly_revenue',
            'avg_price',
            'top3_brand_concentration',  # 明确是品牌集中度
        ],
    }

    # 数值范围检查
    RANGE_CHECKS = {
        'top3_product_concentration': (0, 1),
        'top3_brand_concentration': (0, 1),
        'top10_brand_concentration': (0, 1),
        'new_product_share': (0, 1),
        'avg_price': (0, 10000),
        'top100_monthly_sales': (0, 10000000),
        'top100_monthly_revenue': (0, 1000000000),
    }

    def __init__(self, data_path: str):
        """初始化验证器"""
        self.data_path = Path(data_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.data: Dict = {}

    def load_data(self) -> bool:
        """加载数据文件"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            return True
        except FileNotFoundError:
            self.errors.append(f"文件不存在: {self.data_path}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON 解析错误: {e}")
            return False

    def check_field_naming(self) -> bool:
        """检查字段命名规范"""
        passed = True

        def check_recursive(obj: Any, path: str = ""):
            nonlocal passed
            if isinstance(obj, dict):
                for key in obj.keys():
                    current_path = f"{path}.{key}" if path else key
                    # 检查禁止的字段名
                    if key in self.FORBIDDEN_FIELDS:
                        self.errors.append(
                            f"[命名错误] {current_path}: 使用了模糊的字段名 '{key}'。"
                            f"{self.FORBIDDEN_FIELDS[key]}"
                        )
                        passed = False
                    # 递归检查
                    check_recursive(obj[key], current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_recursive(item, f"{path}[{i}]")

        check_recursive(self.data)
        return passed

    def check_required_fields(self) -> bool:
        """检查必填字段"""
        passed = True

        for section, fields in self.REQUIRED_FIELDS.items():
            if section not in self.data:
                self.errors.append(f"[缺失] 缺少必要区块: {section}")
                passed = False
                continue

            section_data = self.data[section]
            for field in fields:
                if field not in section_data:
                    self.errors.append(f"[缺失] {section}.{field} 是必填字段")
                    passed = False

        return passed

    def check_value_ranges(self) -> bool:
        """检查数值范围"""
        passed = True

        def check_value(obj: Any, path: str = ""):
            nonlocal passed
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if key in self.RANGE_CHECKS and isinstance(value, (int, float)):
                        min_val, max_val = self.RANGE_CHECKS[key]
                        if not (min_val <= value <= max_val):
                            self.errors.append(
                                f"[范围错误] {current_path} = {value}，"
                                f"应在 [{min_val}, {max_val}] 范围内"
                            )
                            passed = False
                    check_value(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_value(item, f"{path}[{i}]")

        check_value(self.data)
        return passed

    def check_consistency(self) -> bool:
        """检查数据一致性"""
        passed = True

        market = self.data.get('market_overview', {})

        # 检查 Top3 品牌集中度是否合理
        top3_brand = market.get('top3_brand_concentration')
        top3_product = market.get('top3_product_concentration')

        if top3_brand and top3_product:
            if top3_brand < top3_product:
                self.warnings.append(
                    f"[一致性警告] top3_brand_concentration ({top3_brand:.2%}) "
                    f"小于 top3_product_concentration ({top3_product:.2%})，"
                    f"这通常不合理（品牌集中度应该 >= 产品集中度）"
                )

        # 检查竞品市场份额之和
        competitors = self.data.get('competitors', [])
        if competitors:
            total_share = 0
            for comp in competitors:
                share_str = comp.get('market_share', '0%')
                try:
                    share = float(share_str.replace('%', '')) / 100
                    total_share += share
                except (ValueError, AttributeError):
                    pass

            if total_share > 1.0:
                self.warnings.append(
                    f"[一致性警告] 竞品市场份额之和 ({total_share:.1%}) 超过 100%"
                )

        return passed

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """执行完整验证"""
        print(f"🔍 验证数据文件: {self.data_path}")
        print("-" * 50)

        # 加载数据
        if not self.load_data():
            return False, self.errors, self.warnings

        # 执行各项检查
        checks = [
            ("字段命名规范", self.check_field_naming),
            ("必填字段", self.check_required_fields),
            ("数值范围", self.check_value_ranges),
            ("数据一致性", self.check_consistency),
        ]

        all_passed = True
        for check_name, check_func in checks:
            passed = check_func()
            status = "✓" if passed else "✗"
            print(f"{status} {check_name}")
            if not passed:
                all_passed = False

        print("-" * 50)

        # 输出警告
        if self.warnings:
            print("\n⚠️ 警告:")
            for warning in self.warnings:
                print(f"  - {warning}")

        # 输出错误
        if self.errors:
            print("\n❌ 错误:")
            for error in self.errors:
                print(f"  - {error}")

        # 总结
        if all_passed and not self.warnings:
            print("\n✅ 所有验证通过！")
        elif all_passed:
            print("\n⚠️ 验证通过，但有警告需要关注")
        else:
            print(f"\n❌ 验证失败，发现 {len(self.errors)} 个错误")

        return all_passed, self.errors, self.warnings


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python validate_data.py <data.json 路径>")
        sys.exit(1)

    data_path = sys.argv[1]
    validator = DataValidator(data_path)
    passed, errors, warnings = validator.validate()

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
