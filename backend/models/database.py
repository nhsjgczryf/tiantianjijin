"""
Database models for fund data storage
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Fund(Base):
    """Fund basic information"""
    __tablename__ = 'funds'
    
    id = Column(Integer, primary_key=True)
    fund_code = Column(String(10), unique=True, nullable=False, index=True)
    fund_name = Column(String(100), nullable=False)
    fund_type = Column(String(50))
    company = Column(String(100))
    manager = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Fund(code={self.fund_code}, name={self.fund_name})>"


class FundValue(Base):
    """Fund daily net value"""
    __tablename__ = 'fund_values'
    
    id = Column(Integer, primary_key=True)
    fund_code = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    net_value = Column(Float)  # 单位净值
    accumulated_value = Column(Float)  # 累计净值
    daily_growth_rate = Column(Float)  # 日增长率
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FundValue(code={self.fund_code}, date={self.date}, value={self.net_value})>"


class FundPerformance(Base):
    """Fund performance metrics"""
    __tablename__ = 'fund_performance'
    
    id = Column(Integer, primary_key=True)
    fund_code = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False)
    week_return = Column(Float)  # 近一周收益率
    month_return = Column(Float)  # 近一月收益率
    quarter_return = Column(Float)  # 近一季度收益率
    half_year_return = Column(Float)  # 近半年收益率
    year_return = Column(Float)  # 近一年收益率
    three_year_return = Column(Float)  # 近三年收益率
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FundPerformance(code={self.fund_code}, date={self.date})>"


# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'funds.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)

def init_db():
    """Initialize database tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    Base.metadata.create_all(engine)
    print(f"Database initialized at {DB_PATH}")

def get_session():
    """Get database session"""
    return Session()
