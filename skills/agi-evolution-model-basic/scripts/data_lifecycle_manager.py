#!/usr/bin/env python3
"""
数据生命周期管理器

负责自动执行归档、压缩、总结等维护任务。

特点：
- 自动化维护（定时或手动触发）
- 可配置的数据生命周期策略
- 完善的错误处理和日志记录
"""

import os
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from metacognition_history import MetacognitionHistoryManager, StorageLayer


@dataclass
class LifecycleConfig:
    """数据生命周期配置"""
    hot_to_warm_days: int = 30          # 热→温转换天数
    warm_to_cold_days: int = 90         # 温→冷转换天数
    cold_to_archive_days: int = 365     # 冷→归档转换天数
    archive_retention_days: int = 1825  # 归档保留天数（5年）
    enable_archive: bool = True         # 是否启用归档
    enable_delete: bool = False         # 是否启用删除过期归档


class DataLifecycleManager:
    """
    数据生命周期管理器
    
    负责自动执行归档、压缩、总结等维护任务。
    """

    def __init__(
        self,
        history_manager: MetacognitionHistoryManager,
        config: Optional[LifecycleConfig] = None
    ):
        self.history_manager = history_manager
        self.config = config or LifecycleConfig()
        
        # 维护日志
        self.maintenance_log = []

    def run_maintenance(self) -> Dict:
        """
        执行维护任务
        
        Returns:
            维护结果统计
        """
        result = {
            'timestamp': datetime.datetime.now().isoformat(),
            'hot_to_warm': 0,
            'warm_to_cold': 0,
            'cold_to_archive': 0,
            'clean_expired_archives': 0,
            'errors': []
        }
        
        today = datetime.datetime.now()
        
        # 1. 热→温转换
        try:
            hot_to_warm_count = self._convert_hot_to_warm(today)
            result['hot_to_warm'] = hot_to_warm_count
        except Exception as e:
            result['errors'].append(f"热→温转换失败: {e}")
        
        # 2. 温→冷转换
        try:
            warm_to_cold_count = self._convert_warm_to_cold(today)
            result['warm_to_cold'] = warm_to_cold_count
        except Exception as e:
            result['errors'].append(f"温→冷转换失败: {e}")
        
        # 3. 冷→归档转换
        try:
            cold_to_archive_count = self._convert_cold_to_archive(today)
            result['cold_to_archive'] = cold_to_archive_count
        except Exception as e:
            result['errors'].append(f"冷→归档转换失败: {e}")
        
        # 4. 清理过期归档
        try:
            clean_count = self._clean_expired_archives(today)
            result['clean_expired_archives'] = clean_count
        except Exception as e:
            result['errors'].append(f"清理过期归档失败: {e}")
        
        # 记录维护日志
        self.maintenance_log.append(result)
        
        return result

    def _convert_hot_to_warm(self, today: datetime.datetime) -> int:
        """
        热数据→温数据转换
        
        Args:
            today: 当前日期
        
        Returns:
            转换的文件数量
        """
        cutoff_date = today - datetime.timedelta(days=self.config.hot_to_warm_days)
        cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
        
        # 查找需要转换的热数据文件
        hot_dir = os.path.join(
            self.history_manager.metacognition_dir,
            StorageLayer.HOT.value
        )
        
        files = os.listdir(hot_dir) if os.path.exists(hot_dir) else []
        converted_count = 0
        
        for filename in files:
            # 提取日期
            if filename.startswith('records_') and filename.endswith('.json'):
                record_date = filename.replace('records_', '').replace('.json', '')
                
                # 检查是否需要转换
                if record_date <= cutoff_date_str:
                    print(f"🔥→♨️ 转换热数据到温数据: {record_date}")
                    try:
                        self.history_manager.hot_to_warm(record_date)
                        converted_count += 1
                    except Exception as e:
                        print(f"❌ 转换失败: {e}")
        
        return converted_count

    def _convert_warm_to_cold(self, today: datetime.datetime) -> int:
        """
        温数据→冷数据转换
        
        Args:
            today: 当前日期
        
        Returns:
            转换的文件数量
        """
        cutoff_date = today - datetime.timedelta(days=self.config.warm_to_cold_days)
        cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
        
        # 查找需要转换的温数据文件
        warm_dir = os.path.join(
            self.history_manager.metacognition_dir,
            StorageLayer.WARM.value
        )
        
        files = os.listdir(warm_dir) if os.path.exists(warm_dir) else []
        converted_count = 0
        
        for filename in files:
            # 提取日期
            if filename.startswith('records_') and filename.endswith('.json.gz'):
                record_date = filename.replace('records_', '').replace('.json.gz', '')
                
                # 检查是否需要转换
                if record_date <= cutoff_date_str:
                    print(f"♨️→❄️ 转换温数据到冷数据: {record_date}")
                    try:
                        self.history_manager.warm_to_cold(record_date)
                        converted_count += 1
                    except Exception as e:
                        print(f"❌ 转换失败: {e}")
        
        return converted_count

    def _convert_cold_to_archive(self, today: datetime.datetime) -> int:
        """
        冷数据→归档转换
        
        Args:
            today: 当前日期
        
        Returns:
            转换的文件数量
        """
        cutoff_date = today - datetime.timedelta(days=self.config.cold_to_archive_days)
        cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
        
        # 查找需要转换的冷数据文件
        cold_dir = os.path.join(
            self.history_manager.metacognition_dir,
            StorageLayer.COLD.value
        )
        
        files = os.listdir(cold_dir) if os.path.exists(cold_dir) else []
        converted_count = 0
        
        for filename in files:
            # 提取日期
            if filename.startswith('stats_') and filename.endswith('.json.gz'):
                record_date = filename.replace('stats_', '').replace('.json.gz', '')
                
                # 检查是否需要转换
                if record_date <= cutoff_date_str:
                    print(f"❄️→📦 归档冷数据: {record_date}")
                    try:
                        if self.config.enable_archive:
                            self.history_manager.cold_to_archive(record_date)
                            converted_count += 1
                        elif self.config.enable_delete:
                            # 删除文件
                            filepath = os.path.join(cold_dir, filename)
                            os.remove(filepath)
                            print(f"🗑️ 删除冷数据: {record_date}")
                            converted_count += 1
                    except Exception as e:
                        print(f"❌ 转换失败: {e}")
        
        return converted_count

    def _clean_expired_archives(self, today: datetime.datetime) -> int:
        """
        清理过期归档
        
        Args:
            today: 当前日期
        
        Returns:
            删除的文件数量
        """
        cutoff_date = today - datetime.timedelta(days=self.config.archive_retention_days)
        cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
        
        # 查找过期的归档文件
        archive_dir = os.path.join(
            self.history_manager.metacognition_dir,
            StorageLayer.ARCHIVE.value
        )
        
        deleted_count = 0
        
        if not os.path.exists(archive_dir):
            return deleted_count
        
        # 遍历所有年份目录
        for year_dir in os.listdir(archive_dir):
            year_path = os.path.join(archive_dir, year_dir)
            
            if not os.path.isdir(year_path):
                continue
            
            # 遍历归档文件
            for filename in os.listdir(year_path):
                # 提取日期
                if filename.startswith('stats_') and filename.endswith('.json.gz'):
                    record_date = filename.replace('stats_', '').replace('.json.gz', '')
                    
                    # 检查是否过期
                    if record_date <= cutoff_date_str:
                        print(f"🗑️ 删除过期归档: {year_dir}/{filename}")
                        try:
                            filepath = os.path.join(year_path, filename)
                            os.remove(filepath)
                            deleted_count += 1
                        except Exception as e:
                            print(f"❌ 删除失败: {e}")
        
        return deleted_count

    def get_maintenance_summary(self) -> Dict:
        """
        获取维护摘要
        
        Returns:
            维护摘要
        """
        if not self.maintenance_log:
            return {
                'total_maintenance_runs': 0,
                'last_maintenance': None,
                'total_conversions': 0,
                'total_errors': 0
            }
        
        last_run = self.maintenance_log[-1]
        
        total_conversions = (
            sum(run['hot_to_warm'] for run in self.maintenance_log) +
            sum(run['warm_to_cold'] for run in self.maintenance_log) +
            sum(run['cold_to_archive'] for run in self.maintenance_log) +
            sum(run['clean_expired_archives'] for run in self.maintenance_log)
        )
        
        total_errors = sum(len(run['errors']) for run in self.maintenance_log)
        
        return {
            'total_maintenance_runs': len(self.maintenance_log),
            'last_maintenance': last_run['timestamp'],
            'total_conversions': total_conversions,
            'total_errors': total_errors
        }

    def get_storage_stats(self) -> Dict:
        """
        获取存储统计
        
        Returns:
            存储统计
        """
        stats = {
            'hot': {'file_count': 0, 'total_size': 0},
            'warm': {'file_count': 0, 'total_size': 0},
            'cold': {'file_count': 0, 'total_size': 0},
            'archive': {'file_count': 0, 'total_size': 0}
        }
        
        for layer in StorageLayer:
            layer_dir = os.path.join(
                self.history_manager.metacognition_dir,
                layer.value
            )
            
            if not os.path.exists(layer_dir):
                continue
            
            for root, dirs, files in os.walk(layer_dir):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    
                    if os.path.isfile(filepath):
                        stats[layer.value]['file_count'] += 1
                        stats[layer.value]['total_size'] += os.path.getsize(filepath)
        
        return stats


# 测试代码
if __name__ == '__main__':
    print("=== 数据生命周期管理器（测试模式） ===\n")
    
    # 创建历史管理器
    history_manager = MetacognitionHistoryManager("./test_lifecycle_history")
    
    # 创建生命周期管理器
    config = LifecycleConfig(
        hot_to_warm_days=1,       # 测试用：1天后转换
        warm_to_cold_days=2,      # 测试用：2天后转换
        cold_to_archive_days=3,   # 测试用：3天后转换
        archive_retention_days=5, # 测试用：5天后删除
        enable_archive=True,
        enable_delete=True
    )
    
    lifecycle_manager = DataLifecycleManager(history_manager, config)
    
    print("配置:")
    print(f"  热→温转换天数: {config.hot_to_warm_days}")
    print(f"  温→冷转换天数: {config.warm_to_cold_days}")
    print(f"  冷→归档转换天数: {config.cold_to_archive_days}")
    print(f"  归档保留天数: {config.archive_retention_days}")
    print()
    
    print("执行维护任务:")
    result = lifecycle_manager.run_maintenance()
    print(f"  热→温转换: {result['hot_to_warm']} 个文件")
    print(f"  温→冷转换: {result['warm_to_cold']} 个文件")
    print(f"  冷→归档转换: {result['cold_to_archive']} 个文件")
    print(f"  清理过期归档: {result['clean_expired_archives']} 个文件")
    if result['errors']:
        print(f"  错误: {result['errors']}")
    print()
    
    print("存储统计:")
    stats = lifecycle_manager.get_storage_stats()
    for layer, layer_stats in stats.items():
        size_mb = layer_stats['total_size'] / (1024 * 1024)
        print(f"  {layer}: {layer_stats['file_count']} 个文件, {size_mb:.2f} MB")
    print()
    
    print("维护摘要:")
    summary = lifecycle_manager.get_maintenance_summary()
    print(f"  总维护次数: {summary['total_maintenance_runs']}")
    print(f"  最后维护时间: {summary['last_maintenance']}")
    print(f"  总转换次数: {summary['total_conversions']}")
    print(f"  总错误数: {summary['total_errors']}")
    print()
    
    print("=== 测试完成 ===")
