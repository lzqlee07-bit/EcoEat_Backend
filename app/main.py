import random
import string
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import engine, Base, SessionLocal
from . import models, schemas

app = FastAPI(title="EcoEat Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "EcoEat Backend Running Successfully!"}


# ==================== 业务接口 1：查看商家与盲盒 ====================
@app.get("/stores", response_model=List[schemas.Store])
def get_stores(db: Session = Depends(get_db)):
    return db.query(models.Store).all()


# ==================== 业务接口 2：获取用户信息 ====================
@app.get("/users/{user_id}", response_model=schemas.User)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ==================== 业务接口 3：核心核心！学生下单购买 ====================
@app.post("/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    # 1. 检查用户是否存在
    user = db.query(models.User).filter(models.User.id == order_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # 2. 检查盲盒是否存在，以及库存是否足够
    blind_box = db.query(models.BlindBox).filter(models.BlindBox.id == order_data.blind_box_id).first()
    if not blind_box:
        raise HTTPException(status_code=404, detail="BlindBox not found")
    if blind_box.stock_quantity <= 0:
        raise HTTPException(status_code=400, detail="Oops! This blind box is sold out.")
        
    # 3. 检查学生钱包余额够不够
    if user.acc_balance < blind_box.flash_price:
        raise HTTPException(status_code=400, detail="Insufficient balance! Please top up.")

    # 4. 严格通过！开始扣款、扣库存、加环保绿色积分
    blind_box.stock_quantity -= 1
    user.acc_balance -= blind_box.flash_price
    user.eco_points += 10  # 每次支持临期食品奖励 10 绿色积分

    # 5. 随机生成一个 6 位数的绿色取货凭证码 (例如: EE8392)
    random_code = "EE" + "".join(random.choices(string.digits, k=4))

    # 6. 创建新订单
    new_order = models.Order(
        user_id=user.id,
        box_id=blind_box.id,
        total_amount=blind_box.flash_price,
        pickup_code=random_code
    )
    
    db.add(new_order)
    db.commit()      # 提交事务
    db.refresh(new_order)
    
    return new_order


# ==================== 业务接口 4：查看某个学生的所有订单历史 ====================
@app.get("/users/{user_id}/orders", response_model=List[schemas.OrderResponse])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).order_by(models.Order.order_time.desc()).all()
    return orders


# ==================== 辅助接口：重新初始化数据（含测试用户） ====================
@app.post("/init-data")
def init_test_data(db: Session = Depends(get_db)):
    # 清理旧数据，保证每次调用都能重新干净地初始化
    db.query(models.BlindBox).delete()
    db.query(models.Store).delete()
    db.query(models.User).delete()
    db.commit()
    
    # 1. 创建一个测试学生（自带 50 元巨款）
    test_user = models.User(name="张同学 (Test User)", phone="13812345678", acc_balance=50.0, eco_points=0)
    db.add(test_user)
    db.commit() # 提交以生成 user.id
    
    # 2. 创建商家
    canteen = models.Store(name="学一食堂 (Canteen 1)", location="校园北区一楼", category="Canteen", rating=4.8)
    cafe = models.Store(name="绿岛咖啡 (Green Island Cafe)", location="图书馆旁", category="Cafe", rating=4.5)
    bakery = models.Store(name="美味面包工坊 (Eco Bakery)", location="学生公寓B栋下", category="Bakery", rating=4.7)
    
    db.add_all([canteen, cafe, bakery])
    db.commit()
    
    # 3. 为商家添加盲盒
    box1 = models.BlindBox(store_id=canteen.id, name="荤素搭配营养午餐盲盒", original_price=15.0, flash_price=6.9, stock_quantity=5, pickup_deadline="12:30 - 13:00")
    box2 = models.BlindBox(store_id=cafe.id, name="经典美式+随机甜品盲盒", original_price=28.0, flash_price=9.9, stock_quantity=3, pickup_deadline="17:00 - 18:00")
    box3 = models.BlindBox(store_id=bakery.id, name="法式全麦可颂面包盲盒", original_price=22.0, flash_price=7.5, stock_quantity=8, pickup_deadline="20:30 - 21:00")
    
    db.add_all([box1, box2, box3])
    db.commit()
    
    return {
        "message": "Database reset and initialized!",
        "your_test_user_id": test_user.id,
        "tip": f"Please use user_id={test_user.id} to test ordering!"
    }