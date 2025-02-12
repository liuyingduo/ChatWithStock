import akshare as ak
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class StockAnalysisService:
    def __init__(self):
        self.risk_free_rate = 0.03  # 假设无风险利率为3%
        self._data_cache = {}

    def get_stock_metrics(self, symbol: str, start_date: str, end_date: str = None):
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            
        # 获取股票历史数据
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"  # 使用前复权数据
        )
        
        # 计算日收益率
        df['daily_returns'] = df['收盘'].pct_change()
        
        # 计算各项指标
        metrics = {
            'total_return': self._calculate_total_return(df),
            'volatility': self._calculate_volatility(df),
            'sharp_ratio': self._calculate_sharp_ratio(df),
            'max_drawdown': self._calculate_max_drawdown(df),
            'sudden_changes': self._detect_sudden_changes(df),
            'beta': self._calculate_beta(df),
            'daily_stats': self._get_daily_stats(df)
        }
        
        return metrics
    
    def _calculate_total_return(self, df):
        """计算总收益率"""
        total_return = (df['收盘'].iloc[-1] / df['收盘'].iloc[0] - 1) * 100
        return round(total_return, 2)
    
    def _calculate_volatility(self, df):
        """计算年化波动率"""
        daily_vol = df['daily_returns'].std()
        annual_vol = daily_vol * np.sqrt(252) * 100
        return round(annual_vol, 2)
    
    def _calculate_sharp_ratio(self, df):
        """计算夏普比率"""
        daily_returns = df['daily_returns'].mean() * 252
        daily_vol = df['daily_returns'].std() * np.sqrt(252)
        sharp_ratio = (daily_returns - self.risk_free_rate) / daily_vol
        return round(sharp_ratio, 2)
    
    def _calculate_max_drawdown(self, df):
        """计算最大回撤"""
        cumulative = (1 + df['daily_returns']).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdowns = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdowns.min() * 100
        return round(max_drawdown, 2)
    
    def _detect_sudden_changes(self, df):
        """检测突变点（这里定义为单日涨跌幅超过5%的点）"""
        threshold = 5
        sudden_changes = df[abs(df['涨跌幅']) > threshold]
        return [{
            'date': row['日期'],
            'change': round(row['涨跌幅'], 2),
            'price': round(row['收盘'], 2)
        } for _, row in sudden_changes.iterrows()]
    
    def _calculate_beta(self, df):
        """计算贝塔系数（相对于市场）"""
        # 这里需要获取同期的市场指数数据，这里简化处理
        return 1.0
    
    def _get_daily_stats(self, df):
        """获取每日统计数据"""
        return [{
            'date': row['日期'],
            'open': row['开盘'],
            'close': row['收盘'],
            'high': row['最高'],
            'low': row['最低'],
            'volume': row['成交量'],
            'change': row['涨跌幅']
        } for _, row in df.iterrows()]

    def get_basic_metrics(self, symbol: str, start_date: str):
        df = self._get_stock_data(symbol, start_date)
        return {
            'total_return': self._calculate_total_return(df),
            'volatility': self._calculate_volatility(df),
            'sharp_ratio': self._calculate_sharp_ratio(df),
            'max_drawdown': self._calculate_max_drawdown(df),
        }

    def get_price_data(self, symbol: str, start_date: str):
        df = self._get_stock_data(symbol, start_date)
        return {
            'daily_stats': self._get_daily_stats(df)
        }

    def get_sudden_changes(self, symbol: str, start_date: str):
        df = self._get_stock_data(symbol, start_date)
        return {
            'sudden_changes': self._detect_sudden_changes(df)
        }

    def _get_stock_data(self, symbol: str, start_date: str):
        """获取股票数据并缓存"""
        cache_key = f"{symbol}_{start_date}"
        if cache_key not in self._data_cache:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=datetime.now().strftime('%Y%m%d'),
                adjust="qfq"
            )
            df['daily_returns'] = df['收盘'].pct_change()
            self._data_cache[cache_key] = df
        return self._data_cache[cache_key] 