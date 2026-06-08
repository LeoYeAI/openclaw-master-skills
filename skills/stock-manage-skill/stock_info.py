"""
股票信息获取模块
"""

import json
import os
import logging
import requests
from datetime import datetime, timedelta
import akshare as ak
import pandas as pd
import time
import yfinance as yf
import shutil
from config import DATA_DIR

# 配置日志
log_file = os.path.join(DATA_DIR, "logs", f"stock_info_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StockInfoFetcher:
    """股票信息获取器"""

    def __init__(self):
        """初始化"""
        self.data_dir = DATA_DIR
        self.stock_info_dir = os.path.join(self.data_dir, "stock_info")
        os.makedirs(self.stock_info_dir, exist_ok=True)

    def _get_stock_date(self):
        """获取当前日期（YYYYMMDD格式）"""
        return datetime.now().strftime('%Y%m%d')

    def _get_file_path(self, date):
        """
        获取股票信息文件的存储路径（每天一个json文件）

        :param date: 数据日期
        :return: 文件路径
        """
        if date is None:
            date = self._get_stock_date()
        
        # 每天一个json文件，记录所有股票信息
        filename = f"stock_info_{date}.json"
        
        return os.path.join(self.stock_info_dir, f"{date}", filename)

    def _get_market_prefix(self, stock_code):
        """
        根据股票代码获取市场前缀

        :param stock_code: 股票代码（纯代码，不含前缀）
        :return: 市场前缀（sh/sz/hk/us）
        """
        # 美股：纯字母代码
        if stock_code.isalpha():
            return 'us'
        
        # 港股：5位数字代码
        if stock_code.isdigit() and len(stock_code) == 5:
            return 'hk'
        
        # A股：6位数字代码
        if stock_code.isdigit() and len(stock_code) == 6:
            if stock_code.startswith('6'):
                return 'sh'  # 上证
            elif stock_code.startswith('0') or stock_code.startswith('3'):
                return 'sz'  # 深证
        
        return None

    def _fetch_from_tencent_api(self, stock_code):
        """
        从腾讯证券API获取股票信息（优先使用，支持A股、港股、美股）

        :param stock_code: 股票代码（纯代码，如 002594, 03690, TSLA）
        :return: 股票信息字典，失败返回None
        """
        try:
            # 获取市场前缀
            prefix = self._get_market_prefix(stock_code)
            
            if not prefix:
                logger.warning(f"无法识别股票代码 {stock_code} 的市场类型")
                return None
            
            # 构造腾讯API请求URL（添加市场前缀）
            tencent_code = f"{prefix}{stock_code}"
            url = f"https://qt.gtimg.cn/q={tencent_code}"
            
            logger.info(f"尝试从腾讯证券API获取股票 {stock_code} 的信息，URL: {url}")
            response = requests.get(url, timeout=10)
            response.encoding = 'gbk'
            
            if response.status_code == 200:
                content = response.text.strip()
                
                # 检查是否成功获取数据
                if '~' in content and 'pv_none_match' not in content:
                    # 解析腾讯API返回的数据
                    # 去掉前缀和后缀
                    if '=' in content:
                        data_str = content.split('=')[1].strip().strip('"').strip(';')
                    else:
                        data_str = content
                    
                    data_parts = data_str.split('~')
                    
                    # 检查是否有股票名称
                    if len(data_parts) > 1 and data_parts[1]:
                        # 根据市场类型选择不同的字段索引
                        if prefix == 'us':
                            # 美股字段解析（根据实际返回数据调整）
                            # 索引31: 涨跌额, 索引32: 涨跌幅, 索引33: 最高价, 索引34: 最低价, 索引37: 成交额
                            stock_info = {
                                'code': stock_code,
                                'name': data_parts[1],  # 中文名称
                                'current_price': float(data_parts[3]) if len(data_parts) > 3 and data_parts[3] else None,
                                'open_price': float(data_parts[5]) if len(data_parts) > 5 and data_parts[5] else None,
                                'previous_close': float(data_parts[4]) if len(data_parts) > 4 and data_parts[4] else None,
                                'high_price': float(data_parts[33]) if len(data_parts) > 33 and data_parts[33] else None,
                                'low_price': float(data_parts[34]) if len(data_parts) > 34 and data_parts[34] else None,
                                'price_change': float(data_parts[31]) if len(data_parts) > 31 and data_parts[31] else None,
                                'price_change_percent': float(data_parts[32]) if len(data_parts) > 32 and data_parts[32] else None,
                                'volume': int(float(data_parts[6])) if len(data_parts) > 6 and data_parts[6] else None,
                                'turnover': float(data_parts[37]) if len(data_parts) > 37 and data_parts[37] else None,
                                'market': '美股',
                                'data_source': '腾讯证券API'
                            }
                        else:
                            # A股和港股字段解析
                            stock_info = {
                                'code': stock_code,
                                'name': data_parts[1],
                                'current_price': float(data_parts[3]) if len(data_parts) > 3 and data_parts[3] else None,
                                'open_price': float(data_parts[5]) if len(data_parts) > 5 and data_parts[5] else None,
                                'previous_close': float(data_parts[4]) if len(data_parts) > 4 and data_parts[4] else None,
                                'high_price': float(data_parts[33]) if len(data_parts) > 33 and data_parts[33] else None,
                                'low_price': float(data_parts[34]) if len(data_parts) > 34 and data_parts[34] else None,
                                'price_change': float(data_parts[31]) if len(data_parts) > 31 and data_parts[31] else None,
                                'price_change_percent': float(data_parts[32]) if len(data_parts) > 32 and data_parts[32] else None,
                                'volume': int(float(data_parts[36])) if len(data_parts) > 36 and data_parts[36] else None,
                                'turnover': float(data_parts[37]) if len(data_parts) > 37 and data_parts[37] else None,
                                'market': 'A股' if prefix in ['sh', 'sz'] else '港股',
                                'data_source': '腾讯证券API'
                            }
                        
                        logger.info(f"成功从腾讯证券API获取股票 {stock_code} 的信息")
                        return stock_info
                else:
                    logger.warning(f"腾讯证券API返回数据为空或未找到股票: {content[:100]}")
            else:
                logger.warning(f"腾讯证券API返回状态码: {response.status_code}")
            
            return None
        except Exception as e:
            logger.error(f"从腾讯证券API获取股票 {stock_code} 信息失败: {e}")
            return None

    def _fetch_from_sina_api(self, stock_code):
        """
        从新浪财经API获取股票信息

        :param stock_code: 股票代码
        :return: 股票信息字典，失败返回None
        """
        try:
            # 构造新浪API请求URL
            if stock_code.startswith('6'):
                url = f"http://hq.sinajs.cn/list=sh{stock_code}"
            elif stock_code.startswith('0') or stock_code.startswith('3'):
                url = f"http://hq.sinajs.cn/list=sz{stock_code}"
            elif stock_code.startswith('0') and len(stock_code) == 5:
                # 港股代码格式：0xxxx
                url = f"http://hq.sinajs.cn/list=hk{stock_code}"
            elif stock_code.startswith('0') and len(stock_code) == 5:
                # 港股代码格式：0xxxx
                url = f"http://hq.sinajs.cn/list=hk{stock_code}"
            elif stock_code.startswith('0'):
                # 港股代码格式：0xxxx
                url = f"http://hq.sinajs.cn/list=hk{stock_code}"
            elif stock_code.isalpha():
                # 美股代码格式：字母
                url = f"http://hq.sinajs.cn/list=gb_{stock_code}"
            else:
                url = f"http://hq.sinajs.cn/list={stock_code}"
            
            logger.info(f"尝试从新浪财经API获取股票 {stock_code} 的信息...")
            response = requests.get(url, timeout=10)
            response.encoding = 'gbk'
            
            if response.status_code == 200:
                content = response.text
                if 'var hq_str_' in content:
                    # 解析新浪API返回的数据
                    data_str = content.split('"')[1]
                    data_parts = data_str.split(',')
                    
                    if len(data_parts) >= 32:
                        stock_info = {
                            'code': stock_code,
                            'name': data_parts[0],
                            'current_price': float(data_parts[3]) if data_parts[3] else None,
                            'open_price': float(data_parts[1]) if data_parts[1] else None,
                            'previous_close': float(data_parts[2]) if data_parts[2] else None,
                            'high_price': float(data_parts[4]) if data_parts[4] else None,
                            'low_price': float(data_parts[5]) if data_parts[5] else None,
                            'price_change': float(data_parts[3]) - float(data_parts[2]) if data_parts[3] and data_parts[2] else None,
                            'volume': int(data_parts[8]) if data_parts[8] else None,
                            'turnover': float(data_parts[9]) if data_parts[9] else None,
                            'market': 'A股',
                            'data_source': '新浪财经API'
                        }
                        
                        # 判断市场类型
                        if stock_code.startswith('0') and len(stock_code) == 5:
                            stock_info['market'] = '港股'
                        elif stock_code.isalpha():
                            stock_info['market'] = '美股'
                        
                        if stock_info['previous_close'] and stock_info['current_price']:
                            stock_info['price_change_percent'] = round((stock_info['price_change'] / stock_info['previous_close']) * 100, 2)
                        
                        logger.info(f"成功从新浪财经API获取股票 {stock_code} 的信息")
                        return stock_info
            
            return None
        except Exception as e:
            logger.error(f"从新浪财经API获取股票 {stock_code} 信息失败: {e}")
            return None

    def _fetch_from_yfinance(self, stock_code):
        """
        从yfinance库获取美股信息（不使用info方法避免速率限制）

        :param stock_code: 股票代码
        :return: 股票信息字典，失败返回None
        """
        try:
            logger.info(f"尝试从yfinance库获取股票 {stock_code} 的信息...")
            
            # 添加延迟以避免速率限制
            time.sleep(5)
            
            # 使用yfinance获取股票信息
            ticker = yf.Ticker(stock_code)
            
            # 只获取历史数据，不获取info（避免速率限制）
            hist = ticker.history(period='5d')  # 获取最近5天数据
            if not hist.empty:
                latest_data = hist.iloc[-1]
                
                # 使用前一个交易日的收盘价作为昨收价
                previous_close = hist.iloc[-2]['Close'] if len(hist) > 1 else latest_data['Open']
                
                stock_info = {
                    'code': stock_code,
                    'name': f"{stock_code} Stock",  # 不使用info，使用通用名称
                    'current_price': latest_data['Close'],
                    'open_price': latest_data['Open'],
                    'previous_close': previous_close,
                    'high_price': latest_data['High'],
                    'low_price': latest_data['Low'],
                    'price_change': None,  # 稍后计算
                    'volume': int(latest_data['Volume']) if pd.notna(latest_data['Volume']) else None,
                    'turnover': None,  # yfinance不提供成交额
                    'market': '美股',
                    'data_source': 'yfinance库'
                }
                
                # 计算涨跌额和涨跌幅
                if stock_info['previous_close'] and stock_info['current_price']:
                    stock_info['price_change'] = stock_info['current_price'] - stock_info['previous_close']
                    stock_info['price_change_percent'] = round((stock_info['price_change'] / stock_info['previous_close']) * 100, 2)
                
                logger.info(f"成功从yfinance库获取股票 {stock_code} 的信息")
                return stock_info
            
            return None
        except Exception as e:
            logger.error(f"从yfinance库获取股票 {stock_code} 信息失败: {e}")
            return None

    def _fetch_from_akshare_us(self, stock_code):
        """
        从akshare获取美股信息

        :param stock_code: 股票代码
        :return: 股票信息字典，失败返回None
        """
        try:
            logger.info(f"尝试从akshare获取美股 {stock_code} 的信息...")
            
            # 获取美股实时行情
            df = ak.stock_us_spot()
            
            # 查找对应股票
            stock = df[df['代码'] == stock_code]
            
            if not stock.empty:
                stock_data = stock.iloc[0]
                
                stock_info = {
                    'code': stock_code,
                    'name': stock_data['名称'],
                    'current_price': stock_data['最新价'],
                    'open_price': stock_data['今开'],
                    'previous_close': stock_data['昨收'],
                    'high_price': stock_data['最高'],
                    'low_price': stock_data['最低'],
                    'price_change': stock_data['涨跌额'],
                    'price_change_percent': stock_data['涨跌幅'],
                    'volume': stock_data['成交量'],
                    'turnover': stock_data['成交额'],
                    'market': '美股',
                    'data_source': 'akshare'
                }
                
                logger.info(f"成功从akshare获取美股 {stock_code} 的信息")
                return stock_info
            else:
                logger.warning(f"akshare中未找到美股 {stock_code} 的数据")
                return None
                
        except Exception as e:
            logger.error(f"从akshare获取美股 {stock_code} 信息失败: {e}")
            return None

    def _fetch_from_yahoo_api(self, stock_code):
        """
        从Yahoo Finance API获取美股信息

        :param stock_code: 股票代码
        :return: 股票信息字典，失败返回None
        """
        try:
            # Yahoo Finance API URL
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_code}"
            
            logger.info(f"尝试从Yahoo Finance API获取股票 {stock_code} 的信息...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://finance.yahoo.com/',
                'Origin': 'https://finance.yahoo.com'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('chart') and data['chart'].get('result'):
                    result = data['chart']['result'][0]
                    meta = result.get('meta', {})
                    indicators = result.get('indicators', {})
                    quote = indicators.get('quote', [{}])[0]
                    
                    if meta:
                        stock_info = {
                            'code': stock_code,
                            'name': meta.get('longName', stock_code),
                            'current_price': meta.get('regularMarketPrice'),
                            'open_price': meta.get('regularMarketOpen'),
                            'previous_close': meta.get('previousClose'),
                            'high_price': meta.get('regularMarketDayHigh'),
                            'low_price': meta.get('regularMarketDayLow'),
                            'price_change': meta.get('regularMarketPrice') - meta.get('previousClose') if meta.get('regularMarketPrice') and meta.get('previousClose') else None,
                            'volume': meta.get('regularMarketVolume'),
                            'turnover': None,  # Yahoo Finance不提供成交额
                            'market': '美股',
                            'data_source': 'Yahoo Finance API'
                        }
                        
                        if stock_info['previous_close'] and stock_info['current_price']:
                            stock_info['price_change_percent'] = round((stock_info['price_change'] / stock_info['previous_close']) * 100, 2)
                        
                        logger.info(f"成功从Yahoo Finance API获取股票 {stock_code} 的信息")
                        return stock_info
            else:
                logger.warning(f"Yahoo Finance API返回状态码: {response.status_code}")
            
            return None
        except Exception as e:
            logger.error(f"从Yahoo Finance API获取股票 {stock_code} 信息失败: {e}")
            return None

    def _cleanup_old_data(self, days=30):
        """
        清理指定天数之前的旧数据

        :param days: 保留的天数
        :return: 清理的文件数量
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_date_str = cutoff_date.strftime('%Y%m%d')
            
            deleted_count = 0
            
            # 遍历所有日期目录
            for dirname in os.listdir(self.stock_info_dir):
                dirpath = os.path.join(self.stock_info_dir, dirname)
                
                # 只处理日期目录（格式：YYYYMMDD）
                if os.path.isdir(dirpath) and dirname.isdigit() and len(dirname) == 8:
                    # 检查是否需要删除
                    if dirname < cutoff_date_str:
                        # 删除整个日期目录
                        import shutil
                        shutil.rmtree(dirpath)
                        logger.info(f"清理旧数据目录: {dirname}")
                        deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"共清理 {deleted_count} 个旧数据目录（{days}天前）")
            
            return deleted_count
        except Exception as e:
            logger.error(f"清理旧数据失败: {e}")
            return 0

    def _save_stock_info_to_daily_file(self, stock_info_dict, date_str):
        """
        将股票信息保存到每日JSON文件中（更新或添加）

        :param stock_info_dict: 股票信息字典
        :param date_str: 数据日期
        """
        try:
            file_path = self._get_file_path(date_str)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 读取现有数据
            existing_data = {}
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # 更新或添加股票信息
            stock_code = stock_info_dict['code']
            existing_data[stock_code] = stock_info_dict
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"股票 {stock_code} 信息已更新到每日文件")
        except Exception as e:
            logger.error(f"保存股票信息到每日文件失败: {e}")

    def fetch_and_save_stock_info(self, stock_code, date=None):
        """
        获取单个股票的详细信息并保存（优先使用腾讯证券API）

        :param stock_code: 股票代码
        :param date: 数据日期，默认为当前日期
        :return: 股票信息字典
        """
        try:
            # 自动清理超过30天的旧数据
            self._cleanup_old_data(days=30)
            
            date_str = date or self._get_stock_date()
            
            # 优先使用腾讯证券API获取股票信息（支持A股、港股、美股）
            logger.info(f"正在获取股票 {stock_code} 的信息...")
            
            # 尝试从腾讯证券API获取数据
            stock_info_dict = self._fetch_from_tencent_api(stock_code)
            if stock_info_dict:
                stock_info_dict['data_date'] = date_str
                stock_info_dict['fetch_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 保存到文件（每天一个json文件，记录所有股票信息）
                self._save_stock_info_to_daily_file(stock_info_dict, date_str)

                logger.info(f"股票 {stock_code} ({stock_info_dict['name']}) 信息已保存")
                return stock_info_dict
            
            # 如果腾讯证券API失败，尝试其他备用方案
            logger.info(f"腾讯证券API获取失败，尝试备用方案...")
            
            # 判断股票类型
            stock_type = self._get_stock_type(stock_code)
            
            if stock_type == 'A股':
                # 尝试获取单个股票的实时行情（使用雪球接口，更高效）
                try:
                    stock_info = ak.stock_individual_spot_xq(symbol=str(stock_code))
                    if stock_info:
                        # 构造股票信息字典
                        stock_info_dict = {
                            'code': str(stock_code),
                            'name': stock_info.get('name', ''),
                            'current_price': stock_info.get('current_price'),
                            'price_change': stock_info.get('price_change'),
                            'price_change_percent': stock_info.get('price_change_percent'),
                            'open_price': stock_info.get('open_price'),
                            'high_price': stock_info.get('high_price'),
                            'low_price': stock_info.get('low_price'),
                            'previous_close': stock_info.get('previous_close'),
                            'volume': stock_info.get('volume'),
                            'turnover': stock_info.get('turnover'),
                            'market': 'A股',
                            'data_date': date_str,
                            'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'data_source': 'akshare雪球接口'
                        }
                        
                        # 保存到文件（每天一个json文件，记录所有股票信息）
                        self._save_stock_info_to_daily_file(stock_info_dict, date_str)

                        logger.info(f"股票 {stock_code} ({stock_info_dict['name']}) 信息已保存")
                        return stock_info_dict
                except Exception as e:
                    logger.error(f"获取股票 {stock_code} 实时行情失败: {e}")
                    
                # 尝试获取单个股票的历史数据（使用东方财富接口）
                try:
                    stock_history = ak.stock_zh_a_hist(symbol=str(stock_code), period="daily", start_date=date_str, end_date=date_str)
                    if not stock_history.empty:
                        row = stock_history.iloc[0]
                        # 构造股票信息字典
                        stock_info_dict = {
                            'code': str(stock_code),
                            'name': '',  # 无法从历史数据中获取股票名称
                            'current_price': float(row['收盘']) if not pd.isna(row['收盘']) else None,
                            'open_price': float(row['开盘']) if not pd.isna(row['开盘']) else None,
                            'high_price': float(row['最高']) if not pd.isna(row['最高']) else None,
                            'low_price': float(row['最低']) if not pd.isna(row['最低']) else None,
                            'volume': int(row['成交量']) if not pd.isna(row['成交量']) else None,
                            'turnover': float(row['成交额']) if not pd.isna(row['成交额']) else None,
                            'market': 'A股',
                            'data_date': date_str,
                            'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'data_source': 'akshare东方财富接口'
                        }
                        
                        # 保存到文件（每天一个json文件，记录所有股票信息）
                        self._save_stock_info_to_daily_file(stock_info_dict, date_str)

                        logger.info(f"股票 {stock_code} 信息已保存")
                        return stock_info_dict
                except Exception as e:
                    logger.error(f"获取股票 {stock_code} 历史数据失败: {e}")
                    
            elif stock_type == '港股':
                # 尝试从新浪财经API获取港股数据
                stock_info_dict = self._fetch_from_sina_api(stock_code)
                if stock_info_dict:
                    stock_info_dict['data_date'] = date_str
                    stock_info_dict['fetch_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 保存到文件（每天一个json文件，记录所有股票信息）
                    self._save_stock_info_to_daily_file(stock_info_dict, date_str)

                    logger.info(f"股票 {stock_code} ({stock_info_dict['name']}) 信息已保存")
                    return stock_info_dict
                
            elif stock_type == '美股':
                # 美股使用多渠道获取数据
                logger.info(f"美股 {stock_code} 使用多渠道获取数据...")
                
                # 优先使用akshare（国内访问快，稳定）
                stock_info_dict = self._fetch_from_akshare_us(stock_code)
                if stock_info_dict:
                    stock_info_dict['data_date'] = date_str
                    stock_info_dict['fetch_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 保存到文件（每天一个json文件，记录所有股票信息）
                    self._save_stock_info_to_daily_file(stock_info_dict, date_str)

                    logger.info(f"股票 {stock_code} ({stock_info_dict['name']}) 信息已保存")
                    return stock_info_dict
                
                # 备选：使用yfinance库
                stock_info_dict = self._fetch_from_yfinance(stock_code)
                if stock_info_dict:
                    stock_info_dict['data_date'] = date_str
                    stock_info_dict['fetch_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 保存到文件（每天一个json文件，记录所有股票信息）
                    self._save_stock_info_to_daily_file(stock_info_dict, date_str)

                    logger.info(f"股票 {stock_code} ({stock_info_dict['name']}) 信息已保存")
                    return stock_info_dict
                
                # 最后备选：使用Yahoo Finance API
                stock_info_dict = self._fetch_from_yahoo_api(stock_code)
                if stock_info_dict:
                    stock_info_dict['data_date'] = date_str
                    stock_info_dict['fetch_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 保存到文件（每天一个json文件，记录所有股票信息）
                    self._save_stock_info_to_daily_file(stock_info_dict, date_str)

                    logger.info(f"股票 {stock_code} ({stock_info_dict['name']}) 信息已保存")
                    return stock_info_dict
                
            # 尝试从新浪财经API获取数据
            stock_info_dict = self._fetch_from_sina_api(stock_code)
            if stock_info_dict:
                stock_info_dict['data_date'] = date_str
                stock_info_dict['fetch_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 保存到文件
                file_path = self._get_file_path(stock_code, date_str)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(stock_info_dict, f, ensure_ascii=False, indent=2)

                logger.info(f"股票 {stock_code} ({stock_info_dict['name']}) 信息已保存到: {file_path}")
                return stock_info_dict
                
            logger.warning(f"未找到股票 {stock_code} 的数据，请检查网络连接或股票代码是否正确")
            return None
                
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 信息失败: {e}")
            return None

    def _get_stock_type(self, stock_code):
        """
        根据股票代码判断股票类型

        :param stock_code: 股票代码
        :return: 股票类型（A股、港股、美股）
        """
        if stock_code.isalpha():
            return '美股'
        elif stock_code.startswith('0') and len(stock_code) == 5:
            return '港股'
        elif stock_code.startswith('6'):
            return 'A股'
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            return 'A股'
        else:
            return 'A股'

    def _get_latest_file_path(self, stock_code, date=None):
        """
        获取指定股票的最新文件路径

        :param stock_code: 股票代码
        :param date: 数据日期，默认为最新日期
        :return: 文件路径
        """
        try:
            if date is None:
                # 查找最新日期
                info_dir = self.stock_info_dir
                if not os.path.exists(info_dir):
                    return None

                dates = [d for d in os.listdir(info_dir) if os.path.isdir(os.path.join(info_dir, d))]
                if not dates:
                    return None

                date = sorted(dates)[-1]

            date_dir = os.path.join(self.stock_info_dir, date)
            if not os.path.exists(date_dir):
                return None

            # 查找指定股票的最新文件（按时间戳排序）
            stock_files = []
            for filename in os.listdir(date_dir):
                if filename.startswith(f"{stock_code}_") and filename.endswith('.json'):
                    filepath = os.path.join(date_dir, filename)
                    stock_files.append(filepath)

            if not stock_files:
                return None

            # 返回最新的文件（按修改时间排序）
            latest_file = max(stock_files, key=os.path.getmtime)
            return latest_file

        except Exception as e:
            logger.error(f"获取股票 {stock_code} 最新文件路径失败: {e}")
            return None

    def get_stock_info(self, stock_code, date=None):
        """
        获取已保存的股票信息

        :param stock_code: 股票代码
        :param date: 数据日期，默认为最新日期
        :return: 股票信息字典
        """
        try:
            file_path = self._get_latest_file_path(stock_code, date)

            if not file_path or not os.path.exists(file_path):
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"获取股票 {stock_code} 信息失败: {e}")
            return None