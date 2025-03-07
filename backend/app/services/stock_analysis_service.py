import akshare as ak
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from functools import lru_cache
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockAnalysisService:
    def __init__(self):
        self.risk_free_rate = 0.03  # 假设无风险利率为3%
        self._data_cache = {}
        self._cache_expiry = {}  # 缓存过期时间
        self._cache_duration = 3600  # 缓存有效期（秒）

    def get_stock_metrics(self, symbol: str, start_date: str, end_date: str = None):
        """获取股票的所有指标"""
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
                
            # 获取股票历史数据
            df = self._get_stock_data(symbol, start_date, end_date)
            
            # 计算各项指标
            metrics = {
                'total_return': self._calculate_total_return(df),
                'volatility': self._calculate_volatility(df),
                'sharp_ratio': self._calculate_sharp_ratio(df),
                'max_drawdown': self._calculate_max_drawdown(df),
                'sudden_changes': self._detect_sudden_changes(df),
                'beta': self._calculate_beta(df, symbol),
                'daily_stats': self._get_daily_stats(df)
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating metrics for {symbol}: {str(e)}")
            raise Exception(f"无法计算股票 {symbol} 的指标: {str(e)}")
    
    def _calculate_total_return(self, df):
        """计算总收益率"""
        if df.empty or len(df) < 2:
            return 0.0
        total_return = (df['收盘'].iloc[-1] / df['收盘'].iloc[0] - 1) * 100
        return round(total_return, 2)
    
    def _calculate_volatility(self, df):
        """计算年化波动率"""
        if df.empty or len(df) < 2:
            return 0.0
        daily_vol = df['daily_returns'].std()
        annual_vol = daily_vol * np.sqrt(252) * 100
        return round(annual_vol, 2)
    
    def _calculate_sharp_ratio(self, df):
        """计算夏普比率"""
        if df.empty or len(df) < 2:
            return 0.0
        daily_returns = df['daily_returns'].mean() * 252
        daily_vol = df['daily_returns'].std() * np.sqrt(252)
        if daily_vol == 0:
            return 0.0
        sharp_ratio = (daily_returns - self.risk_free_rate) / daily_vol
        return round(sharp_ratio, 2)
    
    def _calculate_max_drawdown(self, df):
        """计算最大回撤"""
        if df.empty or len(df) < 2:
            return 0.0
        cumulative = (1 + df['daily_returns'].fillna(0)).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdowns = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdowns.min() * 100
        return round(max_drawdown, 2)
    
    def _detect_sudden_changes(self, df):
        """检测突变点（这里定义为单日涨跌幅超过5%的点）"""
        if df.empty:
            return []
        threshold = 5
        sudden_changes = df[abs(df['涨跌幅']) > threshold]
        # 限制返回最近的10个突变点
        sudden_changes = sudden_changes.tail(10)
        return [{
            'date': row['日期'],
            'change': round(row['涨跌幅'], 2),
            'price': round(row['收盘'], 2)
        } for _, row in sudden_changes.iterrows()]
    
    def _calculate_beta(self, df, symbol):
        """计算贝塔系数（相对于市场）"""
        try:
            # 获取上证指数作为市场基准
            market_df = self._get_market_index(df.index[0].strftime('%Y%m%d'), df.index[-1].strftime('%Y%m%d'))
            
            # 计算市场和股票的日收益率
            market_returns = market_df['收盘'].pct_change().dropna()
            stock_returns = df['daily_returns'].dropna()
            
            # 确保日期对齐
            aligned_data = pd.concat([stock_returns, market_returns], axis=1).dropna()
            
            if aligned_data.empty or len(aligned_data) < 2:
                return 1.0
                
            # 计算协方差和方差
            covariance = aligned_data.iloc[:, 0].cov(aligned_data.iloc[:, 1])
            market_variance = aligned_data.iloc[:, 1].var()
            
            if market_variance == 0:
                return 1.0
                
            beta = covariance / market_variance
            return round(beta, 2)
        except Exception as e:
            logger.warning(f"Error calculating beta for {symbol}: {str(e)}")
            return 1.0
    
    @lru_cache(maxsize=20)
    def _get_market_index(self, start_date, end_date):
        """获取市场指数数据（上证指数）"""
        try:
            df = ak.stock_zh_index_daily(symbol="sh000001", start_date=start_date, end_date=end_date)
            return df
        except Exception as e:
            logger.warning(f"Error fetching market index: {str(e)}")
            # 返回空DataFrame，保持结构一致
            return pd.DataFrame(columns=['日期', '开盘', '收盘', '最高', '最低', '成交量'])
    
    def _get_daily_stats(self, df):
        """获取每日统计数据"""
        if df.empty:
            return []
        return [{
            'date': row['日期'],
            'close': round(float(row['收盘']), 2),
            'volume': int(row['成交量']),
            'change': round(float(row['涨跌幅']), 2)
        } for _, row in df.iterrows()]

    def get_basic_metrics(self, symbol: str, start_date: str):
        """获取基本指标"""
        try:
            logger.info(f"Fetching basic metrics for {symbol} from {start_date}")
            df = self._get_stock_data(symbol, start_date)
            return {
                'total_return': self._calculate_total_return(df),
                'volatility': self._calculate_volatility(df),
                'sharp_ratio': self._calculate_sharp_ratio(df),
                'max_drawdown': self._calculate_max_drawdown(df),
            }
        except Exception as e:
            logger.error(f"Error getting basic metrics for {symbol}: {str(e)}")
            raise Exception(f"获取股票 {symbol} 的基本指标失败: {str(e)}")

    def get_price_data(self, symbol: str, start_date: str):
        """获取价格数据"""
        try:
            df = self._get_stock_data(symbol, start_date)
            return {
                'daily_stats': self._get_daily_stats(df)
            }
        except Exception as e:
            logger.error(f"Error getting price data for {symbol}: {str(e)}")
            raise Exception(f"获取股票 {symbol} 的价格数据失败: {str(e)}")

    def get_sudden_changes(self, symbol: str, start_date: str):
        """获取突变点数据"""
        try:
            df = self._get_stock_data(symbol, start_date)
            return {
                'sudden_changes': self._detect_sudden_changes(df)
            }
        except Exception as e:
            logger.error(f"Error getting sudden changes for {symbol}: {str(e)}")
            raise Exception(f"获取股票 {symbol} 的突变点数据失败: {str(e)}")

    def _get_stock_data(self, symbol: str, start_date: str, end_date: str = None):
        """获取股票数据并缓存"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            
        cache_key = f"{symbol}_{start_date}_{end_date}"
        current_time = time.time()
        
        # 检查缓存是否有效
        if (cache_key in self._data_cache and 
            cache_key in self._cache_expiry and 
            current_time < self._cache_expiry[cache_key]):
            logger.info(f"Using cached data for {symbol}")
            return self._data_cache[cache_key]
        
        # 缓存无效或不存在，重新获取数据
        try:
            logger.info(f"Fetching new data for {symbol} from {start_date} to {end_date}")
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            
            # 确保数据不为空
            if df.empty:
                raise Exception(f"No data available for {symbol} in the specified date range")
                
            # 计算日收益率
            df['daily_returns'] = df['收盘'].pct_change()
            
            # 更新缓存
            self._data_cache[cache_key] = df
            self._cache_expiry[cache_key] = current_time + self._cache_duration
            
            # 清理过期缓存
            self._clean_cache(current_time)
            
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            raise Exception(f"获取股票 {symbol} 的数据失败: {str(e)}")
    
    def _clean_cache(self, current_time):
        """清理过期缓存"""
        expired_keys = [k for k, v in self._cache_expiry.items() if current_time > v]
        for key in expired_keys:
            if key in self._data_cache:
                del self._data_cache[key]
            del self._cache_expiry[key]
        
        # 如果缓存过大，删除最旧的项
        if len(self._data_cache) > 50:  # 最多保留50个缓存项
            oldest_keys = sorted(self._cache_expiry.items(), key=lambda x: x[1])[:10]  # 删除10个最旧的
            for key, _ in oldest_keys:
                if key in self._data_cache:
                    del self._data_cache[key]
                if key in self._cache_expiry:
                    del self._cache_expiry[key] 