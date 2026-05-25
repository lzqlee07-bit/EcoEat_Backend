from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- 盲盒 (BlindBox) 规范 ---
class BlindBoxBase(BaseModel):
    name: str
    original_price: float
    flash_price: float
    stock_quantity: int
    pickup_deadline: str

class BlindBox(BlindBoxBase):
    id: int
    store_id: int

    class Config:
        from_attributes = True  # 允许 Pydantic 直接读取 SQLAlchemy 模型

# --- 商家 (Store) 规范 ---
class StoreBase(BaseModel):
    name: str
    location: Optional[str] = None
    category: Optional[str] = None

class Store(StoreBase):
    id: int
    rating: float
    blind_boxes: List[BlindBox] = []  # 商家详情里包含它拥有的盲盒列表

    class Config:
        from_attributes = True