from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ✨ 关键：必须导入这个跨域工具！
from sqlalchemy.orm import Session
from typing import List

from .database import engine, Base, SessionLocal
from . import models, schemas

app = FastAPI(title="EcoEat Backend API")

# 配置 CORS 跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许任何前端本地环境访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有请求方式 (GET, POST等)
    allow_headers=["*"],  # 允许所有请求头
)

# 自动建表
Base.metadata.create_all(bind=engine)

# 数据库连接依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "EcoEat Backend Running Successfully!"}

# 接口 1：获取商家和盲盒列表
@app.get("/stores", response_model=List[schemas.Store])
def get_stores(db: Session = Depends(get_db)):
    stores = db.query(models.Store).all()
    return stores

# 接口 2：初始化测试数据接口
@app.post("/init-data")
def init_test_data(db: Session = Depends(get_db)):
    if db.query(models.Store).first():
        return {"message": "Database already initialized with data!"}
    
    # 1. 创建商家
    canteen = models.Store(name="学一食堂 (Canteen 1)", location="校园北区一楼", category="Canteen", rating=4.8)
    cafe = models.Store(name="绿岛咖啡 (Green Island Cafe)", location="图书馆旁", category="Cafe", rating=4.5)
    bakery = models.Store(name="美味面包工坊 (Eco Bakery)", location="学生公寓B栋下", category="Bakery", rating=4.7)
    
    db.add_all([canteen, cafe, bakery])
    db.commit()
    
    # 2. 为商家添加盲盒
    box1 = models.BlindBox(store_id=canteen.id, name="荤素搭配营养午餐盲盒", original_price=15.0, flash_price=6.9, stock_quantity=5, pickup_deadline="12:30 - 13:00")
    box2 = models.BlindBox(store_id=cafe.id, name="经典美式+随机甜品盲盒", original_price=28.0, flash_price=9.9, stock_quantity=3, pickup_deadline="17:00 - 18:00")
    box3 = models.BlindBox(store_id=bakery.id, name="法式全麦可颂面包盲盒", original_price=22.0, flash_price=7.5, stock_quantity=8, pickup_deadline="20:30 - 21:00")
    
    db.add_all([box1, box2, box3])
    db.commit()
    
    return {"message": "Test data initialized successfully! 3 stores and 3 blind boxes created."}