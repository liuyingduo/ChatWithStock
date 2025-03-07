from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from .api import chat, stock
from .services.stock_service import StockService
from .services.chat_service import ChatService
from .models.stock import Stock
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os
import logging
from contextlib import asynccontextmanager
import time

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# MongoDB配置
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "chatwithstock")

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
        logger.info("Connecting to MongoDB...")
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        logger.info("MongoDB connection successful")
        
        db = client[DB_NAME]
        stock_service = StockService(client)
        chat_service = ChatService(stock_service)
        chat.init_router(chat_service)
        stock.init_router(stock_service)
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        if client:
            logger.info("Closing MongoDB connection")
            client.close()

app = FastAPI(
    title="ChatWithStock API", 
    description="股票分析和聊天API",
    version="1.0.0",
    lifespan=lifespan
)

# 请求计时中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request to {request.url.path} processed in {process_time:.4f} seconds")
    return response

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"}
    )

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 前端开发服务器
        "http://localhost:4173",  # 前端预览服务器
        os.getenv("FRONTEND_URL", "")  # 生产环境前端URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(stock.router, prefix="/api/stock", tags=["stock"])

# 确保设置了必要的环境变量
if not os.getenv("DASHSCOPE_API_KEY"):
    logger.warning("DASHSCOPE_API_KEY环境变量未设置")

@app.get("/")
async def read_root():
    return {"message": "Welcome to ChatWithStock API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 检查MongoDB连接
        if client:
            await client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "detail": str(e)}
        )

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
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
