from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# 1. 学生/用户表
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False) # 登录账号
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    password_hash = Column(String(128), nullable=False)        # 加密密码存储
    acc_balance = Column(Float, default=0.0)
    eco_points = Column(Integer, default=0)

    # 关联关系
    orders = relationship("Order", back_populates="user")


# 2. 商家表
class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(255))
    category = Column(String(50))
    rating = Column(Float, default=5.0)

    # 关联关系
    blind_boxes = relationship("BlindBox", back_populates="store")


# 3. 盲盒表
class BlindBox(Base):
    __tablename__ = "blind_boxes"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    name = Column(String(100), nullable=False)
    original_price = Column(Float, nullable=False)
    flash_price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    pickup_deadline = Column(String(100))

    # 关联关系
    store = relationship("Store", back_populates="blind_boxes")
    orders = relationship("Order", back_populates="blind_box")


# 4. 订单表
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    box_id = Column(Integer, ForeignKey("blind_boxes.id"))
    order_time = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    pickup_code = Column(String(20), unique=True)

    # 关联关系
    user = relationship("User", back_populates="orders")
    blind_box = relationship("BlindBox", back_populates="orders")