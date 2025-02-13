# app/models.py
from sqlalchemy import Column, Integer, Float, Date, BigInteger
from app.database import Base
import datetime

class OrderRecord(Base):
    __tablename__ = "order_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    date = Column(Date, default=datetime.date.today, index=True)
    order_count = Column(Integer, nullable=False)
    total_nominal = Column(Float, nullable=False)
    tips = Column(Float, default=0)

class ExpenseRecord(Base):
    __tablename__ = "expense_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    date = Column(Date, default=datetime.date.today, index=True)
    expense_amount = Column(Float, nullable=False)