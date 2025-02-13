# app/routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import get_order_records_by_date, get_expense_records_by_date
from app.schemas import OrderRecordSchema, ExpenseRecordSchema
from datetime import date
from typing import List

router = APIRouter()

@router.get("/orders/{user_id}/{report_date}", response_model=List[OrderRecordSchema])
def get_orders(user_id: int, report_date: date, db: Session = Depends(get_db)):
    return get_order_records_by_date(db, user_id, report_date)

@router.get("/expenses/{user_id}/{report_date}", response_model=List[ExpenseRecordSchema])
def get_expenses(user_id: int, report_date: date, db: Session = Depends(get_db)):
    return get_expense_records_by_date(db, user_id, report_date)
