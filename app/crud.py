# app/crud.py
from sqlalchemy.orm import Session
from app.models import OrderRecord, ExpenseRecord
from datetime import datetime


def delete_order_record(db: Session, record_id: int, user_id: int):
    record = db.query(OrderRecord).filter(OrderRecord.id == record_id, OrderRecord.user_id == user_id).first()
    if record:
        db.delete(record)
        db.commit()
        return True
    return False

def delete_expense_record(db: Session, record_id: int, user_id: int):
    record = db.query(ExpenseRecord).filter(ExpenseRecord.id == record_id, ExpenseRecord.user_id == user_id).first()
    if record:
        db.delete(record)
        db.commit()
        return True
    return False

def edit_order_record(db: Session, record_id: int, user_id: int, field: str, new_value: float):
    record = db.query(OrderRecord).filter(OrderRecord.id == record_id, OrderRecord.user_id == user_id).first()
    if record:
        if field == "order":
            record.order_count = int(new_value)
        elif field == "nominal":
            record.total_nominal = new_value
        elif field == "tips":
            record.tips = new_value
        db.commit()
        return True
    return False


def edit_expense_record(db: Session, record_id: int, user_id: int, new_value: float):
    record = db.query(ExpenseRecord).filter(ExpenseRecord.id == record_id, ExpenseRecord.user_id == user_id).first()
    if record:
        record.expense_amount = new_value
        db.commit()
        return True
    return False


def get_order_records_by_date_range(db: Session, user_id: int, start_date, end_date):
    return db.query(OrderRecord).filter(
        OrderRecord.user_id == user_id,
        OrderRecord.date >= start_date,
        OrderRecord.date <= end_date
    ).all()

def get_expense_records_by_date_range(db: Session, user_id: int, start_date, end_date):
    return db.query(ExpenseRecord).filter(
        ExpenseRecord.user_id == user_id,
        ExpenseRecord.date >= start_date,
        ExpenseRecord.date <= end_date
    ).all()


def add_order_record(db: Session, user_id: int, order_count: int, total_nominal: float, tips: float):
    new_order = OrderRecord(
        user_id=user_id,
        order_count=order_count,
        total_nominal=total_nominal,
        tips=tips
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

def add_expense_record(db: Session, user_id: int, expense_amount: float, expense_date: str):
    """
    expense_date: diharapkan dalam format DD-MM-YY
    """
    try:
        # Konversi string tanggal ke objek date
        dt = datetime.strptime(expense_date, "%d-%m-%y").date()
    except ValueError:
        raise ValueError("Format tanggal expense tidak valid. Harus DD-MM-YY.")
    new_expense = ExpenseRecord(
        user_id=user_id,
        expense_amount=expense_amount,
        date=dt
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

def get_order_records_by_date(db: Session, user_id: int, date):
    return db.query(OrderRecord).filter(OrderRecord.user_id == user_id, OrderRecord.date == date).all()

def get_expense_records_by_date(db: Session, user_id: int, date):
    return db.query(ExpenseRecord).filter(ExpenseRecord.user_id == user_id, ExpenseRecord.date == date).all()
