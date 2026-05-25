from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- 1. 盲盒 (BlindBox) 规范 ---
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
        from_attributes = True

# --- 2. 商家 (Store) 规范 ---
class StoreBase(BaseModel):
    name: str
    location: Optional[str] = None
    category: Optional[str] = None

class Store(StoreBase):
    id: int
    rating: float
    blind_boxes: List[BlindBox] = []

    class Config:
        from_attributes = True

# --- 3. 用户 (User) 规范 ---
class UserBase(BaseModel):
    name: str
    phone: Optional[str] = None

class User(UserBase):
    id: int
    eco_points: int
    acc_balance: float

    class Config:
        from_attributes = True

# --- 4. 订单 (Order) 规范 ---
# 前端下单时只需要传：谁买了哪个盲盒
class OrderCreate(BaseModel):
    user_id: int
    blind_box_id: int

# 后端返回给前端的完整订单信息
class OrderResponse(BaseModel):
    id: int
    user_id: int
    box_id: int
    order_time: datetime
    total_amount: float
    pickup_code: str
    blind_box: BlindBox  # 嵌套盲盒信息，方便前端直接展示盲盒名字和价格

    class Config:
        from_attributes = True