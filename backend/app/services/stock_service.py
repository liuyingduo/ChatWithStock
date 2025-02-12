from motor.motor_asyncio import AsyncIOMotorClient
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from ..models.stock import Stock, StockHistory
from scipy import stats

class StockService:
    def __init__(self, client: AsyncIOMotorClient):
        self.db = client.chatwithstock
        self.collection = self.db.stocks

    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # 获取历史数据
        hist = stock.history(period="1y")
        
        # 计算技术指标
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # 年化波动率
        sharpe_ratio = (returns.mean() * 252 - 0.02) / volatility  # 夏普比率
        beta = self._calculate_beta(hist['Close'], symbol)
        
        # 预测未来走势
        prediction = self._predict_future_prices(hist['Close'])
        
        stock_data = {
            "basic_info": {
                "symbol": symbol,
                "name": info.get("longName", ""),
                "current_price": info.get("currentPrice", 0.0),
                "change": info.get("regularMarketChange", 0.0),
                "change_percent": info.get("regularMarketChangePercent", 0.0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "volume": info.get("volume", 0)
            },
            "technical_indicators": {
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "beta": beta,
                "rsi": self._calculate_rsi(hist['Close']),
                "macd": self._calculate_macd(hist['Close'])
            },
            "historical_data": {
                "dates": hist.index.strftime('%Y-%m-%d').tolist(),
                "prices": hist['Close'].tolist(),
                "volumes": hist['Volume'].tolist()
            },
            "predictions": {
                "dates": prediction["dates"],
                "prices": prediction["prices"]
            }
        }
        
        # 更新数据库
        await self.collection.update_one(
            {"symbol": symbol},
            {"$set": {
                "last_updated": datetime.now(),
                **stock_data
            }},
            upsert=True
        )
        
        return stock_data

    def _calculate_beta(self, prices: pd.Series, symbol: str) -> float:
        # 获取市场指数数据
        if symbol.endswith('.SS'):
            market = yf.download('^SSE', start=prices.index[0], end=prices.index[-1])
        else:
            market = yf.download('^SZSE', start=prices.index[0], end=prices.index[-1])
        
        # 计算收益率
        stock_returns = prices.pct_change().dropna()
        market_returns = market['Close'].pct_change().dropna()
        
        # 对齐数据
        aligned_data = pd.concat([stock_returns, market_returns], axis=1).dropna()
        
        # 计算beta
        beta = np.cov(aligned_data.iloc[:,0], aligned_data.iloc[:,1])[0,1] / np.var(aligned_data.iloc[:,1])
        return beta

    def _calculate_rsi(self, prices: pd.Series, periods: int = 14) -> float:
        returns = prices.diff()
        gains = returns.clip(lower=0)
        losses = -returns.clip(upper=0)
        
        avg_gain = gains.rolling(window=periods).mean()
        avg_loss = losses.rolling(window=periods).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def _calculate_macd(self, prices: pd.Series) -> Dict[str, float]:
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return {
            "macd": macd.iloc[-1],
            "signal": signal.iloc[-1],
            "histogram": macd.iloc[-1] - signal.iloc[-1]
        }

    def _predict_future_prices(self, prices: pd.Series) -> Dict[str, List]:
        # 简单的时间序列预测
        days = 7
        last_price = prices.iloc[-1]
        trend = (prices.iloc[-1] - prices.iloc[-20]) / 20  # 计算趋势
        
        future_dates = [
            (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            for i in range(1, days + 1)
        ]
        
        predicted_prices = [
            last_price + trend * i + np.random.normal(0, prices.std() * 0.1)
            for i in range(1, days + 1)
        ]
        
        return {
            "dates": future_dates,
            "prices": predicted_prices
        }

    async def get_risk_analysis(self, symbol: str) -> Dict[str, Any]:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1y")
        
        returns = hist['Close'].pct_change().dropna()
        
        var_95 = np.percentile(returns, 5)  # 95% VaR
        cvar_95 = returns[returns <= var_95].mean()  # 95% CVaR
        
        return {
            "value_at_risk": abs(var_95),
            "conditional_var": abs(cvar_95),
            "max_drawdown": self._calculate_max_drawdown(hist['Close']),
            "downside_risk": self._calculate_downside_risk(returns)
        }

    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        cummax = prices.cummax()
        drawdown = (prices - cummax) / cummax
        return abs(drawdown.min())

    def _calculate_downside_risk(self, returns: pd.Series) -> float:
        # 计算下行风险（低于0的收益率的标准差）
        negative_returns = returns[returns < 0]
        return negative_returns.std() * np.sqrt(252)

    async def get_historical_data(self, symbol: str, period: str = "1mo") -> List[StockHistory]:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        return [
            StockHistory(
                date=index,
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row["Volume"]
            )
            for index, row in hist.iterrows()
        ] 