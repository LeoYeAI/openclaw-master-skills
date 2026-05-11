#!/usr/bin/env python3
"""
Tushare API 客户端

封装 Tushare Pro API，提供简洁易用的接口
"""

import os
import pandas as pd
import tushare as ts
from typing import Optional, List, Union, Dict
from pathlib import Path
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TushareAPI:
    """Tushare API 客户端"""

    def __init__(self, token: Optional[str] = None):
        """
        初始化 API 客户端

        Args:
            token: Tushare Token，默认从环境变量 TUSHARE_TOKEN 读取
        """
        self.token = token or os.getenv('TUSHARE_TOKEN')
        if not self.token:
            raise ValueError(
                "未找到 Tushare Token。请设置环境变量 TUSHARE_TOKEN 或传入 token 参数。\n"
                "获取 Token: https://tushare.pro"
            )

        # 初始化 Tushare API
        self.pro = ts.pro_api(self.token)
        logger.info("Tushare API 客户端初始化成功")

    # ==================== 股票数据 ====================

    def get_stock_daily(
        self,
        ts_code: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        查询股票日线行情

        Args:
            ts_code: 股票代码（如 "000001.SZ"）
            start_date: 开始日期（格式：YYYY-MM-DD 或 YYYYMMDD）
            end_date: 结束日期（格式：YYYY-MM-DD 或 YYYYMMDD）

        Returns:
            pd.DataFrame: 日线数据
        """
        # 统一日期格式
        start_date = self._format_date(start_date)
        end_date = self._format_date(end_date)

        logger.info(f"查询股票日线: {ts_code} ({start_date} ~ {end_date})")

        df = self.pro.daily(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date
        )

        if df.empty:
            logger.warning(f"未查询到数据: {ts_code}")
        else:
            logger.info(f"查询成功，共 {len(df)} 条记录")

        return df

    def get_stock_info(self, ts_code: str) -> Dict:
        """
        查询股票基本信息

        Args:
            ts_code: 股票代码

        Returns:
            dict: 股票基本信息
        """
        logger.info(f"查询股票信息: {ts_code}")

        df = self.pro.stock_basic(
            ts_code=ts_code,
            fields='ts_code,name,area,industry,market,list_date'
        )

        if df.empty:
            logger.warning(f"未查询到股票信息: {ts_code}")
            return {}

        return df.iloc[0].to_dict()

    def get_stock_list(self, market: Optional[str] = None) -> pd.DataFrame:
        """
        查询股票列表

        Args:
            market: 市场类型（主板、创业板、科创板、CDR），None 表示全部

        Returns:
            pd.DataFrame: 股票列表
        """
        logger.info(f"查询股票列表: market={market}")

        df = self.pro.stock_basic(market=market)
        logger.info(f"查询成功，共 {len(df)} 只股票")

        return df

    # ==================== 财务数据 ====================

    def get_financial_indicator(
        self,
        ts_code: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        查询财务指标

        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 财务指标数据
        """
        start_date = self._format_date(start_date)
        end_date = self._format_date(end_date)

        logger.info(f"查询财务指标: {ts_code} ({start_date} ~ {end_date})")

        df = self.pro.fina_indicator(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date
        )

        return df

    def get_income_statement(
        self,
        ts_code: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        查询利润表

        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 利润表数据
        """
        start_date = self._format_date(start_date)
        end_date = self._format_date(end_date)

        logger.info(f"查询利润表: {ts_code} ({start_date} ~ {end_date})")

        df = self.pro.income(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date
        )

        return df

    # ==================== 指数数据 ====================

    def get_index_daily(
        self,
        ts_code: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        查询指数日线行情

        Args:
            ts_code: 指数代码（如 "000300.SH"）
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 指数日线数据
        """
        start_date = self._format_date(start_date)
        end_date = self._format_date(end_date)

        logger.info(f"查询指数日线: {ts_code} ({start_date} ~ {end_date})")

        df = self.pro.index_daily(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date
        )

        return df

    def get_index_weight(
        self,
        index_code: str,
        date: str
    ) -> pd.DataFrame:
        """
        查询指数成分权重

        Args:
            index_code: 指数代码
            date: 日期

        Returns:
            pd.DataFrame: 成分权重数据
        """
        date = self._format_date(date)

        logger.info(f"查询指数成分: {index_code} {date}")

        df = self.pro.index_weight(
            index_code=index_code,
            trade_date=date
        )

        return df

    # ==================== 批量查询 ====================

    def batch_query(
        self,
        ts_codes: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, pd.DataFrame]:
        """
        批量查询多只股票

        Args:
            ts_codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            dict: {股票代码: DataFrame}
        """
        logger.info(f"批量查询: {len(ts_codes)} 只股票")

        results = {}
        for i, ts_code in enumerate(ts_codes, 1):
            logger.info(f"进度: {i}/{len(ts_codes)} - {ts_code}")

            try:
                df = self.get_stock_daily(ts_code, start_date, end_date)
                results[ts_code] = df
            except Exception as e:
                logger.error(f"查询失败: {ts_code}, 错误: {e}")
                results[ts_code] = pd.DataFrame()

        success_count = sum(1 for df in results.values() if not df.empty)
        logger.info(f"批量查询完成: 成功 {success_count}/{len(ts_codes)}")

        return results

    # ==================== 数据导出 ====================

    def export_data(
        self,
        df: pd.DataFrame,
        output_file: str,
        format: str = 'csv'
    ) -> bool:
        """
        导出数据到文件

        Args:
            df: 数据
            output_file: 输出文件路径
            format: 输出格式（csv, json, excel）

        Returns:
            bool: 是否导出成功
        """
        try:
            if format == 'csv':
                df.to_csv(output_file, index=False)
            elif format == 'json':
                df.to_json(output_file, orient='records', indent=2)
            elif format == 'excel':
                df.to_excel(output_file, index=False)
            else:
                raise ValueError(f"不支持的格式: {format}")

            logger.info(f"数据已导出到: {output_file}")
            return True

        except Exception as e:
            logger.error(f"导出失败: {e}")
            return False

    # ==================== 工具方法 ====================

    @staticmethod
    def _format_date(date_str: str) -> str:
        """
        统一日期格式为 YYYYMMDD

        Args:
            date_str: 日期字符串（支持 YYYY-MM-DD 或 YYYYMMDD）

        Returns:
            str: YYYYMMDD 格式的日期
        """
        if '-' in date_str:
            return date_str.replace('-', '')
        return date_str


if __name__ == "__main__":
    # 示例用法
    api = TushareAPI()

    # 查询股票数据
    df = api.get_stock_daily("000001.SZ", "2024-01-01", "2024-12-31")
    print(df.head())

    # 查询股票信息
    info = api.get_stock_info("000001.SZ")
    print(info)
