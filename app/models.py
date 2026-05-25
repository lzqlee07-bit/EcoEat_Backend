from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# 1. 用户 / 学生表
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    eco_points = Column(Integer, default=0)
    acc_balance = Column(Float, default=0.0)  # 对应 ER 图中的账户余额

    # 建立与订单的一对多关系
    orders = relationship("Order", back_populates="user")


# 2. 商家表 (食堂、咖啡厅等)
class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(255))            # 商家位置
    rating = Column(Float, default=5.0)       # 评分
    category = Column(String(50))             # 类别 (如 Canteen, Cafe, Bakery)

    # 一个商家可以提供多个盲盒
    blind_boxes = relationship("BlindBox", back_populates="store")


# 3. 盲盒表
class BlindBox(Base):
    __tablename__ = "blind_boxes"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id")) # 外键连接到商家
    name = Column(String(100), nullable=False)
    original_price = Column(Float, nullable=False)      # 原价
    flash_price = Column(Float, nullable=False)         # 盲盒现价
    stock_quantity = Column(Integer, default=0)         # 库存数量
    pickup_deadline = Column(String(100))               # 取货截止时间 (如 "18:45 - 19:15")

    # 关系映射
    store = relationship("Store", back_populates="blind_boxes")
    orders = relationship("Order", back_populates="blind_box")


# 4. 订单表
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))       # 谁下的单
    box_id = Column(Integer, ForeignKey("blind_boxes.id"))  # 买了哪个盲盒
    order_time = Column(DateTime, default=datetime.utcnow)  # 下单时间
    total_amount = Column(Float, nullable=False)            # 实际支付金额
    pickup_code = Column(String(50))                        # 取货码 (对应UI上的QR码/消费凭证)

    # 关系映射
    user = relationship("User", back_populates="orders")
    blind_box = relationship("BlindBox", back_populates="orders")
    review = relationship("Review", back_populates="order", uselist=False) # 一对一评价


# 5. 评价表
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))     # 对应哪个订单
    rating = Column(Float, nullable=False)                  # 星级评分
    comment = Column(String(500))                           # 评论内容
    photo_url = Column(String(255))                         # 评价配图 URL

    # 关系映射
    order = relationship("Order", back_populates="review")