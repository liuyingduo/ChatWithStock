from typing import List, Dict, Any
import re
from ..models.stock import Stock
from .stock_service import StockService
from ..utils.tools import client, tools, execute_function
import json

class ChatService:
    def __init__(self, stock_service: StockService):
        self.stock_service = stock_service
        self.system_prompt = """你是一个专业的股票投资顾问，擅长：
        1. 股票基本面分析
        2. 技术指标解读
        3. 风险评估
        4. 投资建议
        请用专业且易懂的语言回答用户问题，必要时使用markdown格式美化回复。"""

    async def process_message(self, message: str) -> Dict[str, Any]:
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message}
            ]

            completion = client.chat.completions.create(
                model="qwen-plus",
                messages=messages,
                tools=tools
            )

            response = completion.choices[0].message
            final_response = response.content
            data = None

            # 处理股票相关查询
            if any(keyword in message for keyword in ["股票", "股价", "分析", "预测", "风险"]):
                stock_code = self._extract_stock_code(message)
                if stock_code:
                    try:
                        # 获取综合数据
                        stock_data = await self.stock_service.get_stock_data(stock_code)
                        risk_data = await self.stock_service.get_risk_analysis(stock_code)
                        
                        # 格式化markdown响应
                        final_response = self._format_analysis_response(
                            stock_data, 
                            risk_data,
                            message
                        )
                        
                        # 准备图表数据
                        data = {
                            "chartData": {
                                "dates": stock_data["historical_data"]["dates"],
                                "prices": stock_data["historical_data"]["prices"],
                                "volumes": stock_data["historical_data"]["volumes"],
                                "predictions": stock_data["predictions"]["prices"]
                            },
                            "metrics": self._format_metrics(stock_data, risk_data)
                        }
                    except Exception as e:
                        final_response += f"\n\n获取股票数据时出现错误：{str(e)}"

            return {
                "role": "assistant",
                "content": final_response,
                "data": data
            }

        except Exception as e:
            return {
                "role": "assistant",
                "content": f"抱歉，处理您的请求时出现错误：{str(e)}"
            }

    def _format_analysis_response(
        self, 
        stock_data: Dict[str, Any], 
        risk_data: Dict[str, Any],
        query: str
    ) -> str:
        basic = stock_data["basic_info"]
        tech = stock_data["technical_indicators"]
        
        response = f"""## {basic['name']} ({basic['symbol']}) 分析报告

### 基本信息
- 当前价格：¥{basic['current_price']:.2f}
- 涨跌幅：{basic['change_percent']:.2f}%
- 成交量：{basic['volume']:,}
- 市值：¥{basic['market_cap']:,.0f}
- 市盈率：{basic['pe_ratio']:.2f}

### 技术指标
- RSI (14日)：{tech['rsi']:.2f}
- MACD：{tech['macd']['macd']:.2f}
- Beta系数：{tech['beta']:.2f}
- 波动率：{tech['volatility']*100:.2f}%
- 夏普比率：{tech['sharpe_ratio']:.2f}

### 风险评估
- 最大回撤：{risk_data['max_drawdown']*100:.2f}%
- 下行风险：{risk_data['downside_risk']*100:.2f}%
- 95% VaR：{risk_data['value_at_risk']*100:.2f}%
"""

        # 根据查询内容添加相应的分析
        if "预测" in query or "趋势" in query:
            response += "\n### 趋势预测\n"
            response += "根据历史数据和技术指标分析，预计未来7天的价格走势如上图所示。"
            
        if "风险" in query:
            response += "\n### 风险提示\n"
            risk_level = "高" if tech['volatility'] > 0.3 else "中" if tech['volatility'] > 0.2 else "低"
            response += f"该股票当前风险等级为{risk_level}，主要考虑因素：\n"
            response += f"- 波动率（{tech['volatility']*100:.1f}%）\n"
            response += f"- Beta系数（{tech['beta']:.2f}）\n"
            response += f"- 最大回撤（{risk_data['max_drawdown']*100:.1f}%）\n"

        return response

    def _format_metrics(
        self, 
        stock_data: Dict[str, Any], 
        risk_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        basic = stock_data["basic_info"]
        tech = stock_data["technical_indicators"]
        
        return [
            {
                "name": "当前价格",
                "value": f"¥{basic['current_price']:.2f}",
                "change": basic['change_percent']
            },
            {
                "name": "技术强度",
                "value": "强势" if tech['rsi'] > 70 else "弱势" if tech['rsi'] < 30 else "中性",
                "description": f"RSI: {tech['rsi']:.1f}"
            },
            {
                "name": "风险等级",
                "value": "高" if tech['volatility'] > 0.3 else "中" if tech['volatility'] > 0.2 else "低",
                "description": f"波动率: {tech['volatility']*100:.1f}%"
            },
            {
                "name": "投资评级",
                "value": "推荐" if tech['sharpe_ratio'] > 1 else "谨慎" if tech['sharpe_ratio'] > 0 else "观望",
                "description": f"夏普比率: {tech['sharpe_ratio']:.2f}"
            }
        ]

    def _extract_stock_code(self, message: str) -> str:
        patterns = [
            r'([0-9]{6})',  # 匹配6位数字
            r'贵州茅台',     # 特定股票名称匹配
        ]
        
        stock_code_map = {
            "贵州茅台": "600519.SS",
            "腾讯控股": "0700.HK",
            "阿里巴巴": "9988.HK",
            "平安银行": "000001.SZ",
            "五粮液": "000858.SZ"
        }
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                matched_text = match.group()
                if matched_text in stock_code_map:
                    return stock_code_map[matched_text]
                return matched_text + (".SS" if matched_text[0] == "6" else ".SZ")
        
        # 检查股票名称映射
        for name, code in stock_code_map.items():
            if name in message:
                return code
        
        return "" 