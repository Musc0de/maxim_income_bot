# app/schemas.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class OrderRecordSchema(BaseModel):
    id: int
    user_id: int
    date: date
    order_count: int
    total_nominal: float
    tips: Optional[float] = 0

    class Config:
        from_attributes = True

class ExpenseRecordSchema(BaseModel):
    id: int
    user_id: int
    date: date
    expense_amount: float

    class Config:
        from_attributes = True
