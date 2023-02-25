from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


PG_DSN = "postgresql+asyncpg://app:1234@127.0.0.1:5431/netology"
engine = create_async_engine(PG_DSN)
Base = declarative_base()


Session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


class Ad(Base):
    __tablename__ = "app_ads"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(String(100), nullable=False, unique=False)
    description = Column(String(300), nullable=False, unique=False)
    creation_time = Column(DateTime, server_default=func.now(), unique=False)
    owner = Column(String(50), unique=False)
