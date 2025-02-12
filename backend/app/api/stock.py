from fastapi import APIRouter, HTTPException
from ..services.stock_service import StockService
from ..services.stock_analysis_service import StockAnalysisService
from typing import List

router = APIRouter()
stock_service = None
stock_analysis_service = StockAnalysisService()

def init_router(service: StockService):
    global stock_service
    stock_service = service

@router.get("/{symbol}")
async def get_stock_data(symbol: str):
    try:
        stock_data = await stock_service.get_stock_data(symbol)
        return stock_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

@router.get("/{symbol}/history")
async def get_stock_history(symbol: str, period: str = "1mo"):
    try:
        history_data = await stock_service.get_historical_data(symbol, period)
        return history_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to get history for {symbol}")

@router.get("/analysis/{symbol}")
async def get_stock_analysis(symbol: str, start_date: str):
    try:
        metrics = stock_analysis_service.get_stock_metrics(symbol, start_date)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analysis/{symbol}/basic")
async def get_stock_basic_metrics(symbol: str, start_date: str):
    try:
        print(f"Fetching basic metrics for {symbol} from {start_date}")  # 添加日志
        metrics = stock_analysis_service.get_basic_metrics(symbol, start_date)
        return metrics
    except Exception as e:
        print(f"Error in get_stock_basic_metrics: {str(e)}")  # 添加错误日志
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analysis/{symbol}/price")
async def get_stock_price_data(symbol: str, start_date: str):
    try:
        price_data = stock_analysis_service.get_price_data(symbol, start_date)
        return price_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analysis/{symbol}/changes")
async def get_stock_sudden_changes(symbol: str, start_date: str):
    try:
        changes = stock_analysis_service.get_sudden_changes(symbol, start_date)
        return changes
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 