from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from .api import chat, stock
from .services.stock_service import StockService
from .services.chat_service import ChatService
from .models.stock import Stock
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager

# MongoDB配置
MONGODB_URL = "mongodb://localhost:27017"

# 全局变量声明
client = None
db = None
stock_service = None
chat_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # MongoDB连接
    global client, db, stock_service, chat_service
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        await client.admin.command('ping')
        db = client.chatwithstock
        stock_service = StockService(client)
        chat_service = ChatService(stock_service)
        chat.init_router(chat_service)
        stock.init_router(stock_service)
        yield
    finally:
        if client:
            client.close()

app = FastAPI(title="ChatWithStock API", lifespan=lifespan)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(stock.router, prefix="/api/stock", tags=["stock"])

# 确保设置了必要的环境变量
if not os.getenv("DASHSCOPE_API_KEY"):
    raise ValueError("请设置DASHSCOPE_API_KEY环境变量")

@app.get("/")
async def read_root():
    return {"message": "Welcome to ChatWithStock API"}

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    try:
        stock_data = await stock_service.get_stock_data(symbol)
        return stock_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

@app.get("/api/stock/{symbol}/history")
async def get_stock_history(symbol: str, period: str = "1mo"):
    try:
        history_data = await stock_service.get_historical_data(symbol, period)
        return history_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to get history for {symbol}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
