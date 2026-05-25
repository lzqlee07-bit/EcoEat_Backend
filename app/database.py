from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL  # 引入 URL 工具

# 拆开写，完美避开密码里 @ 符号的解析 Bug
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="20070514Lzq@",  # 你的密码直接写在这里
    host="localhost",
    database="ecoeat_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()