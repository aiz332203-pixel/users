from contextlib import asynccontextmanager
from datetime import datetime
from email.policy import default

from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy import DateTime, func, String, select, Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

#app = FastAPI()

ASYNC_DATABASE_URL="postgresql+asyncpg://postgres:Zhang2003chon@db.etfcuuojykdtdynvyjwd.supabase.co:5432/postgres"


async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)
class Base(DeclarativeBase):
    created_at:Mapped[datetime]=mapped_column(DateTime,insert_default=func.now(),default=func.now(),comment="创建时间")
    updated_at:Mapped[datetime]=mapped_column(DateTime,insert_default=func.now(),default=func.now(),comment="更新时间")

class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(Integer,primary_key=True,comment="用户ID")
    username:Mapped[str] = mapped_column(String(50),unique=True,nullable=False,comment="用户名")
    avatar:Mapped[str]=mapped_column(String(255),comment="头像")
async def create_tables():
    # 获取异步引擎，创建所有表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await async_engine.dispose()
app = FastAPI(lifespan=lifespan)
@app.get("/")
async def root():
    return {"message": "Hello World"}

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,  #绑定异步引擎
    class_=AsyncSession,  #指定会话类
    expire_on_commit=False
)


# 创建依赖项
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session  #返回数据库会话
            await session.commit()  #提交事务
        except Exception:
            await session.rollback()  #回滚事务
            raise
        finally:
            await session.close()  #关闭数据库会话

@app.get("/users")
async def get_user(db:AsyncSession=Depends(get_database)):
    result = await db.execute(select(User))
    users=result.scalars().all()
    return users


