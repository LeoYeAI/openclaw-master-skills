#!/usr/bin/env python3
"""
数据整理自动化脚本
用途: 自动采集、清洗、统计、报告数据
"""

import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import sys


class DataAutomation:
    """数据整理自动化处理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path) if config_path else {}
        self.raw_data: List[Dict] = []
        self.cleaned_data: List[Dict] = []
        self.metrics: Dict[str, Any] = {}
        self.timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    def _load_config(self, path: str) -> Dict:
        """加载配置文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_json(self, filepath: str) -> None:
        """从JSON文件加载数据"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
    
    def load_csv(self, filepath: str) -> None:
        """从CSV文件加载数据"""
        self.raw_data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.raw_data.append(dict(row))
    
    def validate(self) -> bool:
        """数据验证"""
        required_fields = self.config.get('required_fields', [])
        
        if not self.raw_data:
            print("警告: 无数据")
            return False
        
        for item in self.raw_data:
            for field in required_fields:
                if field not in item or not item[field]:
                    print(f"警告: 缺少必填字段 {field}")
        
        return True
    
    def deduplicate(self, key: str = 'id') -> int:
        """去重"""
        seen = set()
        original_count = len(self.cleaned_data)
        
        self.cleaned_data = [
            item for item in self.cleaned_data
            if item.get(key) and item.get(key) not in seen
            and not seen.add(item.get(key))
        ]
        
        removed = original_count - len(self.cleaned_data)
        print(f"去重完成: 移除 {removed} 条重复记录")
        return removed
    
    def clean(self, field_mappings: Optional[Dict] = None) -> None:
        """数据清洗"""
        field_mappings = field_mappings or {}
        
        for item in self.raw_data:
            cleaned = {}
            for key, value in item.items():
                # 应用字段映射
                new_key = field_mappings.get(key, key)
                # 字符串字段去除首尾空格
                if isinstance(value, str):
                    cleaned[new_key] = value.strip()
                else:
                    cleaned[new_key] = value
            self.cleaned_data.append(cleaned)
        
        print(f"清洗完成: {len(self.cleaned_data)} 条有效记录")
    
    def calculate_metrics(self, metric_fields: Optional[List[str]] = None) -> Dict:
        """计算统计指标"""
        metric_fields = metric_fields or []
        self.metrics = {
            'total_records': len(self.cleaned_data),
            'calculation_time': self.timestamp
        }
        
        for field in metric_fields:
            values = []
            for item in self.cleaned_data:
                try:
                    val = float(item.get(field, 0))
                    values.append(val)
                except (ValueError, TypeError):
                    continue
            
            if values:
                self.metrics[f'{field}_sum'] = sum(values)
                self.metrics[f'{field}_avg'] = sum(values) / len(values)
                self.metrics[f'{field}_max'] = max(values)
                self.metrics[f'{field}_min'] = min(values)
                self.metrics[f'{field}_count'] = len(values)
        
        return self.metrics
    
    def generate_report(self, template: Optional[str] = None) -> str:
        """生成报告"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        report = f"""# 数据整理报告 - {date_str}

## 基本统计
- 原始记录数: {len(self.raw_data)}
- 清洗后记录数: {len(self.cleaned_data)}
- 生成时间: {self.timestamp}

## 指标统计
"""
        
        for key, value in self.metrics.items():
            if key not in ['total_records', 'calculation_time']:
                if isinstance(value, float):
                    report += f"- {key}: {value:.2f}\n"
                else:
                    report += f"- {key}: {value}\n"
        
        report += "\n## 最近更新 (前5条)\n"
        for item in self.cleaned_data[-5:]:
            name = item.get('name', item.get('title', 'N/A'))
            report += f"- {name}\n"
        
        return report
    
    def save_results(self, output_dir: str = 'data/processed') -> None:
        """保存结果"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        date_str = datetime.now().strftime('%Y%m%d')
        
        # 保存清洗后的数据
        with open(output_path / f'data_{date_str}.json', 'w', encoding='utf-8') as f:
            json.dump(self.cleaned_data, f, ensure_ascii=False, indent=2)
        
        # 保存报告
        report = self.generate_report()
        with open(output_path / f'report_{date_str}.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 保存指标
        with open(output_path / f'metrics_{date_str}.json', 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存至: {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description='数据整理自动化脚本')
    parser.add_argument('--input', '-i', required=True, help='输入数据文件')
    parser.add_argument('--type', '-t', choices=['json', 'csv'], default='json', help='输入文件类型')
    parser.add_argument('--output', '-o', default='data/processed', help='输出目录')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--key', default='id', help='去重字段')
    parser.add_argument('--metrics', nargs='+', help='需要统计的字段')
    
    args = parser.parse_args()
    
    automator = DataAutomation(config_path=args.config)
    
    print(f"加载数据: {args.input}")
    if args.type == 'json':
        automator.load_json(args.input)
    else:
        automator.load_csv(args.input)
    
    automator.validate()
    automator.clean()
    automator.deduplicate(key=args.key)
    
    if args.metrics:
        metrics = automator.calculate_metrics(metric_fields=args.metrics)
        print("统计指标:", metrics)
    
    automator.save_results(output_dir=args.output)
    print("数据整理完成!")


if __name__ == '__main__':
    main()
