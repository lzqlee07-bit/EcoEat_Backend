from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# 1. 学生/用户表 (对应你的 student 实体)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) # 对应 SID
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    acc_balance = Column(Float, default=0.0)           # 账户余额（之前漏了它）
    eco_points = Column(Integer, default=0)            # 绿色积分

    # 关联关系：一个用户可以有多个订单
    orders = relationship("Order", back_populates="user")


# 2. 商家表 (对应你的 store 实体)
class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True) # 对应 store_ID
    name = Column(String(100), nullable=False)
    location = Column(String(255))
    category = Column(String(50))                      # 比如 Canteen, Cafe
    rating = Column(Float, default=5.0)

    # 关联关系：一个商家可以提供多个盲盒
    blind_boxes = relationship("BlindBox", back_populates="store")


# 3. 盲盒表 (对应你的 blind_box 实体)
class BlindBox(Base):
    __tablename__ = "blind_boxes"

    id = Column(Integer, primary_key=True, index=True) # 对应 box_ID
    store_id = Column(Integer, ForeignKey("stores.id")) # 外键连接商家
    name = Column(String(100), nullable=False)
    original_price = Column(Float, nullable=False)     # 对应 originalPrice
    flash_price = Column(Float, nullable=False)        # 对应 flashPrice
    stock_quantity = Column(Integer, default=0)        # 库存
    pickup_deadline = Column(String(100))              # 对应 pickUpDeadline

    # 关联关系
    store = relationship("Store", back_populates="blind_boxes")
    orders = relationship("Order", back_populates="blind_box")


# 4. 订单表 (对应你的 order 实体)
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True) # 对应 order_ID
    user_id = Column(Integer, ForeignKey("users.id"))
    box_id = Column(Integer, ForeignKey("blind_boxes.id"))
    order_time = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)       # 对应 totalAmount
    pickup_code = Column(String(20), unique=True)      # 对应 pickUpCode

    # 关联关系
    user = relationship("User", back_populates="orders")
    blind_box = relationship("BlindBox", back_populates="orders")