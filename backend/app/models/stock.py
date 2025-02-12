from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StockBase(BaseModel):
    symbol: str
    name: str
    current_price: float
    change: float
    change_percent: float
    
class StockCreate(StockBase):
    pass

class Stock(StockBase):
    id: str
    last_updated: datetime
    
    class Config:
        orm_mode = True

class StockHistory(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int 