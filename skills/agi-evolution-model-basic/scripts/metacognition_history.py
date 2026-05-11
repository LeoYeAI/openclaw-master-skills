#!/usr/bin/env python3
"""
元认知历史管理器（分层存储架构）

提供分层存储功能：
- 热数据层（0-1个月）：JSON格式，快速访问
- 温数据层（1-3个月）：GZIP压缩，节省空间
- 冷数据层（3-12个月）：聚合统计，长期保存
- 归档层（>12个月）：归档存储或删除

特点：
- 自动数据转换（热→温→冷→归档）
- 统一查询接口
- 性能优化（索引、缓存）
"""

import os
import gzip
import json
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class StorageLayer(Enum):
    """存储层级"""
    HOT = "hot"       # 热数据层（0-1个月）
    WARM = "warm"     # 温数据层（1-3个月）
    COLD = "cold"     # 冷数据层（3-12个月）
    ARCHIVE = "archive"  # 归档层（>12个月）


@dataclass
class MetacognitionRecordLite:
    """元认知记录（简化版）"""
    timestamp: str
    context_type: str
    objectivity_score: float
    strategy: str
    success: bool
    learning_stage: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DailyStatistics:
    """日统计（冷数据层）"""
    date: str
    count: int
    avg_objectivity: float
    min_objectivity: float
    max_objectivity: float
    success_rate: float
    strategy_distribution: dict
    context_distribution: dict
    learning_stage: str

    def to_dict(self) -> dict:
        return asdict(self)


class MetacognitionHistoryManager:
    """
    元认知历史管理器
    
    提供分层存储和统一查询接口。
    """

    def __init__(self, base_dir: str = "./agi_memory"):
        self.base_dir = base_dir
        self.metacognition_dir = os.path.join(base_dir, "metacognition_history")
        
        # 创建各层目录
        for layer in StorageLayer:
            layer_dir = os.path.join(self.metacognition_dir, layer.value)
            os.makedirs(layer_dir, exist_ok=True)
        
        # 缓存（热数据层）
        self._cache = {}
        self._cache_max_size = 1000

    def add_record(self, record: MetacognitionRecordLite):
        """
        添加元认知记录
        
        Args:
            record: 元认知记录
        """
        # 获取当前日期
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"records_{date_str}.json"
        filepath = os.path.join(self.metacognition_dir, StorageLayer.HOT.value, filename)
        
        # 读取现有记录
        records = []
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                records = json.load(f)
        
        # 添加新记录
        records.append(record.to_dict())
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        # 更新缓存
        self._cache[filepath] = records

    def query(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        context_type: Optional[str] = None,
        min_success_rate: Optional[float] = None,
        strategy: Optional[str] = None,
        include_detail: bool = False
    ) -> List[Dict]:
        """
        跨层级查询
        
        Args:
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            context_type: 场景类型
            min_success_rate: 最小成功率
            strategy: 策略类型
            include_detail: 是否包含详细记录
        
        Returns:
            查询结果列表
        """
        results = []
        
        # 查询热数据层
        hot_results = self._query_hot_layer({
            'start_date': start_date,
            'end_date': end_date,
            'context_type': context_type,
            'min_success_rate': min_success_rate,
            'strategy': strategy
        })
        results.extend(hot_results)
        
        # 查询温数据层（如果需要详细记录）
        if include_detail:
            warm_results = self._query_warm_layer({
                'start_date': start_date,
                'end_date': end_date,
                'context_type': context_type,
                'min_success_rate': min_success_rate,
                'strategy': strategy
            })
            results.extend(warm_results)
        else:
            # 温数据层仅返回统计信息
            warm_stats = self._query_warm_layer_stats({
                'start_date': start_date,
                'end_date': end_date,
                'context_type': context_type,
                'min_success_rate': min_success_rate,
                'strategy': strategy
            })
            results.extend(warm_stats)
        
        # 查询冷数据层（统计信息）
        cold_results = self._query_cold_layer({
            'start_date': start_date,
            'end_date': end_date,
            'context_type': context_type,
            'min_success_rate': min_success_rate,
            'strategy': strategy
        })
        results.extend(cold_results)
        
        return results

    def _query_hot_layer(self, filters: Dict) -> List[Dict]:
        """查询热数据层"""
        results = []
        
        # 获取热数据层所有文件
        hot_dir = os.path.join(self.metacognition_dir, StorageLayer.HOT.value)
        files = os.listdir(hot_dir) if os.path.exists(hot_dir) else []
        
        for filename in files:
            filepath = os.path.join(hot_dir, filename)
            
            # 从缓存读取
            if filepath in self._cache:
                records = self._cache[filepath]
            else:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        records = json.load(f)
                    self._cache[filepath] = records
                except:
                    continue
            
            # 应用过滤条件
            for record in records:
                if self._matches_filters(record, filters):
                    results.append(record)
        
        return results

    def _query_warm_layer(self, filters: Dict) -> List[Dict]:
        """查询温数据层（详细记录）"""
        results = []
        
        warm_dir = os.path.join(self.metacognition_dir, StorageLayer.WARM.value)
        files = os.listdir(warm_dir) if os.path.exists(warm_dir) else []
        
        for filename in files:
            if not filename.endswith('.gz'):
                continue
            
            filepath = os.path.join(warm_dir, filename)
            
            # 解压缩
            try:
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    records = json.load(f)
            except:
                continue
            
            # 应用过滤条件
            for record in records:
                if self._matches_filters(record, filters):
                    results.append(record)
        
        return results

    def _query_warm_layer_stats(self, filters: Dict) -> List[Dict]:
        """查询温数据层（统计信息）"""
        # 简化实现：返回记录统计
        results = []
        
        warm_dir = os.path.join(self.metacognition_dir, StorageLayer.WARM.value)
        files = os.listdir(warm_dir) if os.path.exists(warm_dir) else []
        
        for filename in files:
            if not filename.endswith('.gz'):
                continue
            
            filepath = os.path.join(warm_dir, filename)
            
            # 解压缩
            try:
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    records = json.load(f)
            except:
                continue
            
            # 应用过滤条件并统计
            filtered_records = [r for r in records if self._matches_filters(r, filters)]
            
            if filtered_records:
                results.append({
                    'date': filename.replace('records_', '').replace('.json.gz', ''),
                    'count': len(filtered_records),
                    'layer': 'warm'
                })
        
        return results

    def _query_cold_layer(self, filters: Dict) -> List[Dict]:
        """查询冷数据层（聚合统计）"""
        results = []
        
        cold_dir = os.path.join(self.metacognition_dir, StorageLayer.COLD.value)
        files = os.listdir(cold_dir) if os.path.exists(cold_dir) else []
        
        for filename in files:
            if not filename.endswith('.gz'):
                continue
            
            filepath = os.path.join(cold_dir, filename)
            
            # 解压缩
            try:
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    stats = json.load(f)
            except:
                continue
            
            # 应用过滤条件
            for stat in stats:
                if self._matches_filters(stat, filters):
                    stat['layer'] = 'cold'
                    results.append(stat)
        
        return results

    def _matches_filters(self, record: Dict, filters: Dict) -> bool:
        """检查记录是否匹配过滤条件"""
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        context_type = filters.get('context_type')
        min_success_rate = filters.get('min_success_rate')
        strategy = filters.get('strategy')
        
        # 日期过滤
        if start_date and record.get('timestamp', '') < start_date:
            return False
        if end_date and record.get('timestamp', '') > end_date:
            return False
        
        # 场景过滤
        if context_type and record.get('context_type') != context_type:
            return False
        
        # 成功率过滤
        if min_success_rate is not None:
            if 'success_rate' in record:
                if record['success_rate'] < min_success_rate:
                    return False
            elif 'success' in record:
                if record['success'] != True:
                    return False
        
        # 策略过滤
        if strategy and record.get('strategy') != strategy:
            return False
        
        return True

    def hot_to_warm(self, record_date: str):
        """
        热数据→温数据转换（压缩）
        
        Args:
            record_date: 记录日期（YYYY-MM-DD）
        """
        hot_filename = f"records_{record_date}.json"
        hot_filepath = os.path.join(self.metacognition_dir, StorageLayer.HOT.value, hot_filename)
        
        if not os.path.exists(hot_filepath):
            return
        
        # 读取热数据
        with open(hot_filepath, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        # 压缩为GZIP
        warm_filename = f"records_{record_date}.json.gz"
        warm_filepath = os.path.join(self.metacognition_dir, StorageLayer.WARM.value, warm_filename)
        
        with gzip.open(warm_filepath, 'wt', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False)
        
        # 删除热数据
        os.remove(hot_filepath)
        
        # 清除缓存
        if hot_filepath in self._cache:
            del self._cache[hot_filepath]
        
        print(f"✅ 热→温转换完成: {record_date}")

    def warm_to_cold(self, record_date: str):
        """
        温数据→冷数据转换（聚合统计）
        
        Args:
            record_date: 记录日期（YYYY-MM-DD）
        """
        warm_filename = f"records_{record_date}.json.gz"
        warm_filepath = os.path.join(self.metacognition_dir, StorageLayer.WARM.value, warm_filename)
        
        if not os.path.exists(warm_filepath):
            return
        
        # 解压缩温数据
        with gzip.open(warm_filepath, 'rt', encoding='utf-8') as f:
            records = json.load(f)
        
        # 按天聚合统计
        daily_stats = {}
        for record in records:
            date = record['timestamp'][:10]
            
            if date not in daily_stats:
                daily_stats[date] = {
                    'date': date,
                    'count': 0,
                    'avg_objectivity': 0.0,
                    'min_objectivity': 1.0,
                    'max_objectivity': 0.0,
                    'success_count': 0,
                    'strategy_distribution': {},
                    'context_distribution': {}
                }
            
            daily_stats[date]['count'] += 1
            daily_stats[date]['avg_objectivity'] += record.get('objectivity_score', 0.0)
            
            if record.get('success', False):
                daily_stats[date]['success_count'] += 1
            
            # 最小/最大客观性
            obj_score = record.get('objectivity_score', 0.0)
            daily_stats[date]['min_objectivity'] = min(
                daily_stats[date]['min_objectivity'], obj_score
            )
            daily_stats[date]['max_objectivity'] = max(
                daily_stats[date]['max_objectivity'], obj_score
            )
            
            # 策略分布
            strategy = record.get('strategy', 'unknown')
            daily_stats[date]['strategy_distribution'][strategy] = \
                daily_stats[date]['strategy_distribution'].get(strategy, 0) + 1
            
            # 场景分布
            context = record.get('context_type', 'unknown')
            daily_stats[date]['context_distribution'][context] = \
                daily_stats[date]['context_distribution'].get(context, 0) + 1
        
        # 计算平均值
        for date, stats in daily_stats.items():
            if stats['count'] > 0:
                stats['avg_objectivity'] /= stats['count']
                stats['success_rate'] = stats['success_count'] / stats['count']
            else:
                stats['success_rate'] = 0.0
        
        # 保存冷数据（压缩）
        cold_filename = f"stats_{record_date}.json.gz"
        cold_filepath = os.path.join(self.metacognition_dir, StorageLayer.COLD.value, cold_filename)
        
        with gzip.open(cold_filepath, 'wt', encoding='utf-8') as f:
            json.dump(list(daily_stats.values()), f, ensure_ascii=False)
        
        # 删除温数据
        os.remove(warm_filepath)
        
        print(f"✅ 温→冷转换完成: {record_date}")

    def cold_to_archive(self, record_date: str):
        """
        冷数据→归档转换
        
        Args:
            record_date: 记录日期（YYYY-MM-DD）
        """
        cold_filename = f"stats_{record_date}.json.gz"
        cold_filepath = os.path.join(self.metacognition_dir, StorageLayer.COLD.value, cold_filename)
        
        if not os.path.exists(cold_filepath):
            return
        
        # 创建归档目录（按年份）
        year = record_date[:4]
        archive_dir = os.path.join(self.metacognition_dir, StorageLayer.ARCHIVE.value, year)
        os.makedirs(archive_dir, exist_ok=True)
        
        # 移动到归档
        archive_filepath = os.path.join(archive_dir, cold_filename)
        shutil.move(cold_filepath, archive_filepath)
        
        print(f"✅ 冷→归档转换完成: {record_date}")


# 测试代码
if __name__ == '__main__':
    print("=== 元认知历史管理器（测试模式） ===\n")
    
    manager = MetacognitionHistoryManager("./test_metacognition_history")
    
    # 测试添加记录
    print("测试1：添加记录")
    record = MetacognitionRecordLite(
        timestamp=datetime.now().isoformat(),
        context_type='scientific',
        objectivity_score=0.85,
        strategy='correct',
        success=True,
        learning_stage='growth'
    )
    manager.add_record(record)
    print("✅ 记录添加成功\n")
    
    # 测试查询
    print("测试2：查询记录")
    results = manager.query(context_type='scientific')
    print(f"查询结果数: {len(results)}")
    for r in results:
        print(f"  - {r.get('timestamp')}: {r.get('context_type')}, {r.get('objectivity_score')}")
    print()
    
    # 测试数据转换
    print("测试3：数据转换")
    today = datetime.now().strftime("%Y-%m-%d")
    manager.hot_to_warm(today)
    print()
    
    print("=== 测试完成 ===")
