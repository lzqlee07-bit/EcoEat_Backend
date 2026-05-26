import random
import string
import hashlib  # 用于密码安全哈希
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import engine, Base, SessionLocal
from . import models, schemas

app = FastAPI(title="EcoEat Backend API with Auth")

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

# 🔒 密码加盐哈希辅助函数
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@app.get("/")
def home():
    return {"message": "EcoEat Backend with Auth Running Successfully!"}


# ==================== 🔑 账户认证接口 ====================

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    # 1. 检查账号是否已存在
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists!")
    
    # 2. 创建新用户，密码加密
    new_user = models.User(
        username=user_data.username,
        name=user_data.name,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        acc_balance=100.0,  # 注册新用户送 100 元初始资金
        eco_points=0
    )
    db.add(new_user)
    db.commit()
    return {"message": "Register successful!", "user_id": new_user.id}


@app.post("/login", response_model=schemas.LoginResponse)
def login_user(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    # 1. 查找用户
    user = db.query(models.User).filter(models.User.username == login_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # 2. 校验加密后的密码
    if user.password_hash != hash_password(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # 3. 登录成功返回凭证
    mock_token = f"eco-token-{user.id}-auth999"
    return {
        "message": "Login successful!",
        "user_id": user.id,
        "name": user.name,
        "token": mock_token
    }


# ==================== 🛍️ 核心业务接口 ====================

@app.get("/stores", response_model=List[schemas.Store])
def get_stores(db: Session = Depends(get_db)):
    return db.query(models.Store).all()


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == order_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    blind_box = db.query(models.BlindBox).filter(models.BlindBox.id == order_data.blind_box_id).first()
    if not blind_box:
        raise HTTPException(status_code=404, detail="BlindBox not found")
    if blind_box.stock_quantity <= 0:
        raise HTTPException(status_code=400, detail="Oops! This blind box is sold out.")
        
    if user.acc_balance < blind_box.flash_price:
        raise HTTPException(status_code=400, detail="Insufficient balance! Please top up.")

    # 扣款扣库存加积分
    blind_box.stock_quantity -= 1
    user.acc_balance -= blind_box.flash_price
    user.eco_points += 10

    # 生成取货凭证码
    random_code = "EE" + "".join(random.choices(string.digits, k=4))

    new_order = models.Order(
        user_id=user.id,
        box_id=blind_box.id,
        total_amount=blind_box.flash_price,
        pickup_code=random_code
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@app.get("/users/{user_id}/orders", response_model=List[schemas.OrderResponse])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Order).filter(models.Order.user_id == user_id).order_by(models.Order.order_time.desc()).all()


# ==================== 🔄 数据初始化接口 ====================

@app.post("/init-data")
def init_test_data(db: Session = Depends(get_db)):
    db.query(models.Order).delete()
    db.query(models.BlindBox).delete()
    db.query(models.Store).delete()
    db.query(models.User).delete()
    db.commit()
    
    # 初始化带登录凭证的测试学生 (账号: student1, 密码: 123456)
    test_user = models.User(
        username="student1",
        name="张同学 (Test User)",
        phone="13812345678",
        password_hash=hash_password("123456"),
        acc_balance=50.0,
        eco_points=0
    )
    db.add(test_user)
    db.commit()
    
    canteen = models.Store(name="学一食堂 (Canteen 1)", location="校园北区一楼", category="Canteen", rating=4.8)
    cafe = models.Store(name="绿岛咖啡 (Green Island Cafe)", location="图书馆旁", category="Cafe", rating=4.5)
    bakery = models.Store(name="美味面包工坊 (Eco Bakery)", location="学生公寓B栋下", category="Bakery", rating=4.7)
    db.add_all([canteen, cafe, bakery])
    db.commit()
    
    box1 = models.BlindBox(store_id=canteen.id, name="荤素搭配营养午餐盲盒", original_price=15.0, flash_price=6.9, stock_quantity=5, pickup_deadline="12:30 - 13:00")
    box2 = models.BlindBox(store_id=cafe.id, name="经典美式+随机甜品盲盒", original_price=28.0, flash_price=9.9, stock_quantity=3, pickup_deadline="17:00 - 18:00")
    box3 = models.BlindBox(store_id=bakery.id, name="法式全麦可颂面包盲盒", original_price=22.0, flash_price=7.5, stock_quantity=8, pickup_deadline="20:30 - 21:00")
    db.add_all([box1, box2, box3])
    db.commit()
    
    return {
        "message": "Database successfully reset with Auth support!",
        "test_account": {
            "username": "student1",
            "password": "123456"
        }
    }