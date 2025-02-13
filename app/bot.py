import asyncio
import logging
import calendar
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.database import SessionLocal
from app.crud import (
    add_order_record,
    add_expense_record,
    get_order_records_by_date_range,
    get_expense_records_by_date_range,
)
from app.config import BOT_TOKEN

# Inisialisasi bot dan dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Main menu dengan opsi input, laporan, hapus, edit, dan batal
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Tambah Order"), KeyboardButton(text="➕ Tambah Pengeluaran")],
        [KeyboardButton(text="📊 Laporan Bulanan"), KeyboardButton(text="📊 Laporan Harian")],
        [KeyboardButton(text="🗑 Hapus Order"), KeyboardButton(text="🗑 Hapus Pengeluaran")],
        [KeyboardButton(text="✏️ Edit Order"), KeyboardButton(text="✏️ Edit Pengeluaran")],
        [KeyboardButton(text="❌ Batal")]
    ],
    resize_keyboard=True
)

# --- Definisi FSM untuk tiap alur ---

# FSM untuk input Order (dengan pemilihan tanggal)
class OrderInput(StatesGroup):
    waiting_for_date = State()
    waiting_for_order_count = State()
    waiting_for_total_nominal = State()
    waiting_for_tips = State()

# FSM untuk input Expense
class ExpenseInput(StatesGroup):
    waiting_for_date = State()
    waiting_for_expense_amount = State()

# FSM untuk laporan Bulanan
class ReportInput(StatesGroup):
    waiting_for_report_date = State()

# FSM untuk laporan Harian
class DailyReportInput(StatesGroup):
    waiting_for_daily_report_date = State()

# FSM untuk menghapus Order (dengan input tanggal)
class DeleteOrder(StatesGroup):
    waiting_for_date = State()
    waiting_for_order_id = State()

# FSM untuk menghapus Expense (dengan input tanggal)
class DeleteExpense(StatesGroup):
    waiting_for_date = State()
    waiting_for_expense_id = State()

# FSM untuk mengedit Order (dengan input tanggal)
class EditOrder(StatesGroup):
    waiting_for_date = State()
    waiting_for_order_id = State()
    waiting_for_field_to_edit = State()
    waiting_for_new_value = State()

# FSM untuk mengedit Expense (dengan input tanggal)
class EditExpense(StatesGroup):
    waiting_for_date = State()
    waiting_for_expense_id = State()
    waiting_for_new_value = State()

# --- Handler Universal untuk Cancel/Back ---
@dp.message(Command("cancel"))
@dp.message(lambda message: message.text and message.text.lower() in ["❌ batal", "cancel", "back", "kembali"])
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Operasi dibatalkan. Kembali ke menu utama.", reply_markup=main_menu)

# --- Handler /start ---
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Selamat datang di Bot Penghitung Maxim!\nPilih menu di bawah:", reply_markup=main_menu)

# --- Flow TAMBAH ORDER (dengan input tanggal) ---
@dp.message(lambda message: message.text == "➕ Tambah Order")
async def initiate_order(message: types.Message, state: FSMContext):
    await state.set_state(OrderInput.waiting_for_date)
    await message.answer(
        "Masukkan tanggal order (format: DD-MM-YY) atau ketik 'hari ini' untuk order hari ini:\n(Ketik '❌ Batal' untuk membatalkan)"
    )

@dp.message(OrderInput.waiting_for_date)
async def process_date_input(message: types.Message, state: FSMContext):
    if message.text is None:
        return
    if message.text.lower() in ["❌ batal", "cancel", "back", "kembali"]:
        await state.clear()
        return await message.answer("🚫 Proses dibatalkan.", reply_markup=main_menu)
    try:
        from datetime import datetime
        if message.text.lower() == "hari ini":
            order_date = datetime.now().strftime("%d-%m-%y")
        else:
            text = message.text.strip()
            # Jika panjang teks 8 karakter, asumsikan format DD-MM-YY
            # Jika panjang teks 10 karakter, asumsikan format DD-MM-YYYY
            if len(text) == 8:
                dt = datetime.strptime(text, "%d-%m-%y")
            elif len(text) == 10:
                dt = datetime.strptime(text, "%d-%m-%Y")
            else:
                raise ValueError("Format tidak dikenali")
            order_date = dt.strftime("%d-%m-%y")
    except ValueError:
        return await message.answer("⚠️ Format tanggal tidak valid! Gunakan format DD-MM-YY atau DD-MM-YYYY, atau ketik 'hari ini'.")
    await state.update_data(order_date=order_date)
    await state.set_state(OrderInput.waiting_for_order_count)
    await message.answer(f"Masukkan jumlah order untuk tanggal {order_date}:\n(Ketik '❌ Batal' untuk membatalkan)")





@dp.message(OrderInput.waiting_for_order_count)
async def process_order_count(message: types.Message, state: FSMContext):
    if message.text is None or not message.text.isdigit():
        return await message.answer("⚠️ Masukkan angka yang valid untuk jumlah order!")
    order_count = int(message.text)
    await state.update_data(order_count=order_count)
    await state.set_state(OrderInput.waiting_for_total_nominal)
    await message.answer("Masukkan total nominal order (misal: 34100):")

@dp.message(OrderInput.waiting_for_total_nominal)
async def process_total_nominal(message: types.Message, state: FSMContext):
    try:
        total_nominal = float(message.text)
        await state.update_data(total_nominal=total_nominal)
        await state.set_state(OrderInput.waiting_for_tips)
        await message.answer("Masukkan total tips (misal: 7700):")
    except ValueError:
        await message.answer("Input tidak valid. Masukkan angka untuk total nominal order:")

@dp.message(OrderInput.waiting_for_tips)
async def process_tips(message: types.Message, state: FSMContext):
    try:
        tips = float(message.text)
        data = await state.get_data()
        order_count = data.get("order_count")
        total_nominal = data.get("total_nominal")
        order_date = data.get("order_date")
        db = SessionLocal()
        add_order_record(db, message.from_user.id, order_count, total_nominal, tips)
        db.close()
        total_pemasukan = total_nominal + tips
        await message.answer(
            f"✅ Order tersimpan untuk tanggal {order_date}!\n\n"
            f"🛵 ORDERAN:\n"
            f"• Jumlah Order: {order_count}\n"
            f"• Total Nominal: Rp{total_nominal:,.0f}\n"
            f"• Total Tips: Rp{tips:,.0f}\n"
            f"• Total Keseluruhan: Rp{total_pemasukan:,.0f}",
            reply_markup=main_menu
        )
        await state.clear()
    except ValueError:
        await message.answer("Input tidak valid. Masukkan angka untuk total tips:")
    except Exception as e:
        await message.answer(f"Terjadi kesalahan: {str(e)}")
        await state.clear()

# --- Flow TAMBAH PENGELUARAN ---
@dp.message(lambda message: message.text == "➕ Tambah Pengeluaran")
async def initiate_expense(message: types.Message, state: FSMContext):
    await state.set_state(ExpenseInput.waiting_for_date)
    await message.answer(
        "Masukkan tanggal pengeluaran (format: DD-MM-YY) atau ketik 'hari ini' untuk pengeluaran hari ini:\n(Ketik '❌ Batal' untuk membatalkan)"
    )


# Handler untuk input tanggal pengeluaran
@dp.message(ExpenseInput.waiting_for_date)
async def process_expense_date(message: types.Message, state: FSMContext):
    if message.text is None:
        return
    if message.text.lower() in ["❌ batal", "cancel", "back", "kembali"]:
        await state.clear()
        return await message.answer("🚫 Proses dibatalkan.", reply_markup=main_menu)
    try:
        from datetime import datetime
        text = message.text.strip()
        if text.lower() == "hari ini":
            expense_date = datetime.now().strftime("%d-%m-%y")
        elif len(text) == 8:
            dt = datetime.strptime(text, "%d-%m-%y")
            expense_date = dt.strftime("%d-%m-%y")
        elif len(text) == 10:
            dt = datetime.strptime(text, "%d-%m-%Y")
            expense_date = dt.strftime("%d-%m-%y")
        else:
            raise ValueError("Format tidak dikenali")
    except ValueError:
        return await message.answer("⚠️ Format tanggal tidak valid! Gunakan format DD-MM-YY atau DD-MM-YYYY, atau ketik 'hari ini'.")
    await state.update_data(expense_date=expense_date)
    await state.set_state(ExpenseInput.waiting_for_expense_amount)
    await message.answer(f"Masukkan total pengeluaran untuk tanggal {expense_date} (misal: 50000):\n(Ketik '❌ Batal' untuk membatalkan)")




@dp.message(ExpenseInput.waiting_for_expense_amount)
async def process_expense_amount(message: types.Message, state: FSMContext):
    try:
        expense_amount = float(message.text)
        data = await state.get_data()
        expense_date = data.get("expense_date")
        db = SessionLocal()
        # Fungsi add_expense_record telah diperbarui untuk menerima parameter tanggal
        add_expense_record(db, message.from_user.id, expense_amount, expense_date)
        db.close()
        await message.answer(
            f"✅ Pengeluaran tersimpan untuk tanggal {expense_date}!\n\n"
            f"💸 PENGELUARAN:\n"
            f"• Total Pengeluaran: Rp{expense_amount:,.0f}",
            reply_markup=main_menu
        )
        await state.clear()
    except ValueError:
        await message.answer("Input tidak valid. Masukkan angka untuk pengeluaran:")
    except Exception as e:
        await message.answer(f"Terjadi kesalahan: {str(e)}")
        await state.clear()




# --- Flow LAPORAN BULANAN ---
@dp.message(lambda message: message.text == "📊 Laporan Bulanan")
async def initiate_monthly_report(message: types.Message, state: FSMContext):
    await state.set_state(ReportInput.waiting_for_report_date)
    await message.answer(
        "Masukkan tanggal laporan (dd-mm-yyyy).\nLaporan akan mencakup seluruh bulan berdasarkan tanggal tersebut.\n(misal: 06-02-2025)",
        reply_markup=main_menu
    )

@dp.message(ReportInput.waiting_for_report_date)
async def process_monthly_report_date(message: types.Message, state: FSMContext):
    try:
        input_date = datetime.datetime.strptime(message.text, "%d-%m-%Y").date()
        year = input_date.year
        month = input_date.month
        first_day = datetime.date(year, month, 1)
        last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])
        db = SessionLocal()
        order_records = get_order_records_by_date_range(db, message.from_user.id, first_day, last_day)
        expense_records = get_expense_records_by_date_range(db, message.from_user.id, first_day, last_day)
        db.close()
        # Kelompokkan data order per hari
        orders_by_date = {}
        for record in order_records:
            day = record.date.strftime("%d-%m-%Y")
            if day not in orders_by_date:
                orders_by_date[day] = {"order_count": 0, "total_nominal": 0.0, "tips": 0.0}
            orders_by_date[day]["order_count"] += record.order_count
            orders_by_date[day]["total_nominal"] += record.total_nominal
            orders_by_date[day]["tips"] += record.tips
        # Kelompokkan data expense per hari
        expenses_by_date = {}
        for record in expense_records:
            day = record.date.strftime("%d-%m-%Y")
            if day not in expenses_by_date:
                expenses_by_date[day] = 0.0
            expenses_by_date[day] += record.expense_amount
        report_message = f"📊 Laporan Bulanan ({month:02d}-{year}):\n\n"
        report_message += "🛵 ORDERAN:\n"
        for day in sorted(orders_by_date.keys(), key=lambda d: datetime.datetime.strptime(d, "%d-%m-%Y")):
            data = orders_by_date[day]
            overall = data["total_nominal"] + data["tips"]
            report_message += f"📅 {day}\n"
            report_message += f"  • Jumlah Order: {data['order_count']}\n"
            report_message += f"  • Total Nominal: Rp{data['total_nominal']:,.0f}\n"
            report_message += f"  • Total Tips: Rp{data['tips']:,.0f}\n"
            report_message += f"  • Total Keseluruhan: Rp{overall:,.0f}\n\n"
        report_message += "💸 PENGELUARAN:\n"
        for day in sorted(expenses_by_date.keys(), key=lambda d: datetime.datetime.strptime(d, "%d-%m-%Y")):
            amount = expenses_by_date[day]
            report_message += f"📅 {day}\n"
            report_message += f"  • Total Pengeluaran: Rp{amount:,.0f}\n\n"
        total_order_count = sum(data["order_count"] for data in orders_by_date.values())
        total_nominal = sum(data["total_nominal"] for data in orders_by_date.values())
        total_tips = sum(data["tips"] for data in orders_by_date.values())
        total_order_overall = total_nominal + total_tips
        total_expense = sum(expenses_by_date.values())
        report_message += "🔍 REKAP TOTAL:\n"
        report_message += f"• Total Pemasukan: Rp{total_order_overall:,.0f}\n"
        report_message += f"• Total Pengeluaran: Rp{total_expense:,.0f}\n"
        net_total = total_order_overall - total_expense
        report_message += f"• Total Bersih: Rp{net_total:,.0f}"
        await message.answer(report_message, reply_markup=main_menu)
        await state.clear()
    except ValueError:
        await message.answer("Format tanggal tidak valid. Gunakan format dd-mm-yyyy.")
    except Exception as e:
        await message.answer(f"Terjadi kesalahan: {str(e)}")
        await state.clear()

# --- Flow LAPORAN HARIAN ---
@dp.message(lambda message: message.text == "📊 Laporan Harian")
async def initiate_daily_report(message: types.Message, state: FSMContext):
    await state.set_state(DailyReportInput.waiting_for_daily_report_date)
    await message.answer(
        "Masukkan tanggal laporan harian (dd-mm-yyyy) atau ketik 'hari ini':",
        reply_markup=main_menu
    )

@dp.message(DailyReportInput.waiting_for_daily_report_date)
async def process_daily_report_date(message: types.Message, state: FSMContext):
    try:
        from datetime import datetime
        if message.text.lower() == "hari ini":
            report_date = datetime.now().date()
        else:
            report_date = datetime.strptime(message.text, "%d-%m-%Y").date()
        db = SessionLocal()
        from app.crud import get_order_records_by_date, get_expense_records_by_date
        order_records = get_order_records_by_date(db, message.from_user.id, report_date)
        expense_records = get_expense_records_by_date(db, message.from_user.id, report_date)
        db.close()
        total_order_count = sum(record.order_count for record in order_records)
        total_nominal = sum(record.total_nominal for record in order_records)
        total_tips = sum(record.tips for record in order_records)
        total_order_overall = total_nominal + total_tips
        total_expense = sum(record.expense_amount for record in expense_records)
        report_message = f"📊 Laporan Harian ({report_date.strftime('%d-%m-%Y')}):\n\n"
        report_message += "🛵 ORDERAN:\n"
        report_message += f"• Jumlah Order: {total_order_count}\n"
        report_message += f"• Total Nominal: Rp{total_nominal:,.0f}\n"
        report_message += f"• Total Tips: Rp{total_tips:,.0f}\n"
        report_message += f"• Total Keseluruhan: Rp{total_order_overall:,.0f}\n\n"
        report_message += "💸 PENGELUARAN:\n"
        report_message += f"• Total Pengeluaran: Rp{total_expense:,.0f}\n\n"
        report_message += "🔍 REKAP TOTAL:\n"
        report_message += f"• Total Pemasukan: Rp{total_order_overall:,.0f}\n"
        report_message += f"• Total Pengeluaran: Rp{total_expense:,.0f}\n"
        net_total = total_order_overall - total_expense
        report_message += f"• Total Bersih: Rp{net_total:,.0f}"
        await message.answer(report_message, reply_markup=main_menu)
        await state.clear()
    except ValueError:
        await message.answer("Format tanggal tidak valid. Gunakan format dd-mm-yyyy.")
    except Exception as e:
        await message.answer(f"Terjadi kesalahan: {str(e)}")
        await state.clear()

# --- Flow HAPUS DATA ORDER ---
@dp.message(lambda message: message.text == "🗑 Hapus Order")
async def initiate_delete_order(message: types.Message, state: FSMContext):
    await state.set_state(DeleteOrder.waiting_for_date)
    await message.answer("Masukkan tanggal order yang ingin dihapus (dd-mm-yyyy) atau ketik 'hari ini':", reply_markup=main_menu)

@dp.message(DeleteOrder.waiting_for_date)
async def process_delete_order_date(message: types.Message, state: FSMContext):
    try:
        from datetime import datetime
        if message.text.lower() == "hari ini":
            order_date = datetime.now().date()
        else:
            order_date = datetime.strptime(message.text, "%d-%m-%Y").date()
    except ValueError:
        return await message.answer("Format tanggal tidak valid. Gunakan format dd-mm-yyyy.")
    await state.update_data(delete_order_date=order_date)
    db = SessionLocal()
    from app.crud import get_order_records_by_date
    orders = get_order_records_by_date(db, message.from_user.id, order_date)
    db.close()
    if orders:
        response = f"Daftar order pada tanggal {order_date.strftime('%d-%m-%Y')}:\n"
        for order in orders:
            response += f"ID: {order.id} | Order: {order.order_count} | Nominal: Rp{order.total_nominal:,.0f} | Tips: Rp{order.tips:,.0f}\n"
        response += "\nMasukkan ID order yang ingin dihapus (atau ketik '❌ Batal' untuk membatalkan):"
        await state.set_state(DeleteOrder.waiting_for_order_id)
        await message.answer(response, reply_markup=main_menu)
    else:
        await message.answer(f"Tidak ada order pada tanggal {order_date.strftime('%d-%m-%Y')}.", reply_markup=main_menu)
        await state.clear()

@dp.message(DeleteOrder.waiting_for_order_id)
async def process_delete_order(message: types.Message, state: FSMContext):
    if message.text.lower() in ["❌ batal", "cancel", "back", "kembali"]:
        await state.clear()
        return await message.answer("🚫 Proses dibatalkan.", reply_markup=main_menu)
    try:
        order_id = int(message.text)
        db = SessionLocal()
        from app.crud import delete_order_record
        success = delete_order_record(db, order_id, message.from_user.id)
        db.close()
        if success:
            await message.answer("Order berhasil dihapus.", reply_markup=main_menu)
        else:
            await message.answer("Order tidak ditemukan atau gagal dihapus.", reply_markup=main_menu)
    except ValueError:
        await message.answer("Input tidak valid. Masukkan angka untuk ID order.")
    except Exception as e:
        await message.answer(f"Terjadi kesalahan: {str(e)}")
    finally:
        await state.clear()

# --- Flow HAPUS DATA PENGELUARAN ---
@dp.message(lambda message: message.text == "🗑 Hapus Pengeluaran")
async def initiate_delete_expense(message: types.Message, state: FSMContext):
    await state.set_state(DeleteExpense.waiting_for_date)
    await message.answer("Masukkan tanggal pengeluaran yang ingin dihapus (dd-mm-yyyy) atau ketik 'hari ini':", reply_markup=main_menu)

@dp.message(DeleteExpense.waiting_for_date)
async def process_delete_expense_date(message: types.Message, state: FSMContext):
    try:
        from datetime import datetime
        if message.text.lower() == "hari ini":
            expense_date = datetime.now().date()
        else:
            expense_date = datetime.strptime(message.text, "%d-%m-%Y").date()
    except ValueError:
        return await message.answer("Format tanggal tidak valid. Gunakan format dd-mm-yyyy.")
    await state.update_data(delete_expense_date=expense_date)
    db = SessionLocal()
    from app.crud import get_expense_records_by_date
    expenses = get_expense_records_by_date(db, message.from_user.id, expense_date)
    db.close()
    if expenses:
        response = f"Daftar pengeluaran pada tanggal {expense_date.strftime('%d-%m-%Y')}:\n"
        for expense in expenses:
            response += f"ID: {expense.id} | Pengeluaran: Rp{expense.expense_amount:,.0f}\n"
        response += "\nMasukkan ID pengeluaran yang ingin dihapus (atau ketik '❌ Batal' untuk membatalkan):"
        await state.set_state(DeleteExpense.waiting_for_expense_id)
        await message.answer(response, reply_markup=main_menu)
    else:
        await message.answer(f"Tidak ada pengeluaran pada tanggal {expense_date.strftime('%d-%m-%Y')}.", reply_markup=main_menu)
        await state.clear()

@dp.message(DeleteExpense.waiting_for_expense_id)
async def process_delete_expense(message: types.Message, state: FSMContext):
    if message.text.lower() in ["❌ batal", "cancel", "back", "kembali"]:
        await state.clear()
        return await message.answer("🚫 Proses dibatalkan.", reply_markup=main_menu)
    try:
        expense_id = int(message.text)
        db = SessionLocal()
        from app.crud import delete_expense_record
        success = delete_expense_record(db, expense_id, message.from_user.id)
        db.close()
        if success:
            await message.answer("Pengeluaran berhasil dihapus.", reply_markup=main_menu)
        else:
            await message.answer("Pengeluaran tidak ditemukan atau gagal dihapus.", reply_markup=main_menu)
    except ValueError:
        await message.answer("Input tidak valid. Masukkan angka untuk ID pengeluaran.")
    except Exception as e:
        await message.answer(f"Terjadi kesalahan: {str(e)}")
    finally:
        await state.clear()

# --- Flow EDIT ORDER ---
@dp.message(lambda message: message.text == "✏️ Edit Order")
async def initiate_edit_order(message: types.Message, state: FSMContext):
    await state.set_state(EditOrder.waiting_for_date)
    await message.answer("Masukkan tanggal order yang ingin diedit (dd-mm-yyyy) atau ketik 'hari ini':", reply_markup=main_menu)

@dp.message(EditOrder.waiting_for_date)
async def process_edit_order_date(message: types.Message, state: FSMContext):
    try:
        from datetime import datetime
        if message.text.lower() == "hari ini":
            edit_date = datetime.now().date()
        else:
            edit_date = datetime.strptime(message.text, "%d-%m-%Y").date()
    except ValueError:
        return await message.answer("Format tanggal tidak valid. Gunakan format dd-mm-yyyy.")
    await state.update_data(edit_order_date=edit_date)
    db = SessionLocal()
    from app.crud import get_order_records_by_date
    orders = get_order_records_by_date(db, message.from_user.id, edit_date)
    db.close()
    if orders:
        response = f"Daftar order pada tanggal {edit_date.strftime('%d-%m-%Y')}:\n"
        for order in orders:
            response += f"ID: {order.id} | Order: {order.order_count} | Nominal: Rp{order.total_nominal:,.0f} | Tips: Rp{order.tips:,.0f}\n"
        response += "\nMasukkan ID order yang ingin diedit (atau ketik '❌ Batal' untuk membatalkan):"
        await state.set_state(EditOrder.waiting_for_order_id)
        await message.answer(response, reply_markup=main_menu)
    else:
        await message.answer(f"Tidak ada order pada tanggal {edit_date.strftime('%d-%m-%Y')}.", reply_markup=main_menu)
        await state.clear()

@dp.message(EditOrder.waiting_for_order_id)
async def process_edit_order_id(message: types.Message, state: FSMContext):
    if message.text.lower() in ["❌ batal", "cancel", "back", "kembali"]:
        await state.clear()
        return await message.answer("🚫 Proses dibatalkan.", reply_markup=main_menu)
    try:
        order_id = int(message.text)
        await state.update_data(order_id=order_id)
        await state.set_state(EditOrder.waiting_for_field_to_edit)
        await message.answer("Pilih field yang ingin diedit: ketik 'order', 'nominal', atau 'tips'")
    except ValueError:
        await message.answer("Input tidak valid. Masukkan angka untuk ID order.")

@dp.message(EditOrder.waiting_for_field_to_edit)
async def process_edit_order_field(message: types.Message, state: FSMContext):
    field = message.text.lower() if message.text else ""
    if field not in ['order', 'nominal', 'tips']:
        return await message.answer("Field tidak valid. Pilih antara 'order', 'nominal', atau 'tips'.")
    await state.update_data(field=field)
    await state.set_state(EditOrder.waiting_for_new_value)
    await message.answer(f"Masukkan nilai baru untuk {field}:")

@dp.message(EditOrder.waiting_for_new_value)
async def process_edit_order_new_value(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        order_id = data.get("order_id")
        field = data.get("field")
        new_value = float(message.text)
        db = SessionLocal()
        from app.crud import edit_order_record
        success = edit_order_record(db, order_id, message.from_user.id, field, new_value)
        db.close()
        if success:
            await message.answer("Order berhasil diperbarui.", reply_markup=main_menu)
        else:
            await message.answer("Gagal memperbarui order. Pastikan ID order benar.", reply_markup=main_menu)
    except ValueError:
        await message.answer("Input tidak valid. Masukkan angka untuk nilai baru.")
    except Exception as e:
        await message.answer(f"Terjadi kesalahan: {str(e)}")
    finally:
        await state.clear()

# --- Flow EDIT PENGELUARAN ---
@dp.message(lambda message: message.text == "✏️ Edit Pengeluaran")
async def initiate_edit_expense(message: types.Message, state: FSMContext):
    await state.set_state(EditExpense.waiting_for_date)
    await message.answer("Masukkan tanggal pengeluaran yang ingin diedit (dd-mm-yyyy) atau ketik 'hari ini':", reply_markup=main_menu)

@dp.message(EditExpense.waiting_for_date)
async def process_edit_expense_date(message: types.Message, state: FSMContext):
    try:
        from datetime import datetime
        if message.text.lower() == "hari ini":
            edit_date = datetime.now().date()
        else:
            edit_date = datetime.strptime(message.text, "%d-%m-%Y").date()
    except ValueError:
        return await message.answer("Format tanggal tidak valid. Gunakan format dd-mm-yyyy.")
    await state.update_data(edit_expense_date=edit_date)
    db = SessionLocal()
    from app.crud import get_expense_records_by_date
    expenses = get_expense_records_by_date(db, message.from_user.id, edit_date)
    db.close()
    if expenses:
        response = f"Daftar pengeluaran pada tanggal {edit_date.strftime('%d-%m-%Y')}:\n"
        for expense in expenses:
            response += f"ID: {expense.id} | Pengeluaran: Rp{expense.expense_amount:,.0f}\n"
        response += "\nMasukkan ID pengeluaran yang ingin diedit (atau ketik '❌ Batal' untuk membatalkan):"
        await state.set_state(EditExpense.waiting_for_expense_id)
        await message.answer(response, reply_markup=main_menu)
    else:
        await message.answer(f"Tidak ada pengeluaran pada tanggal {edit_date.strftime('%d-%m-%Y')}.", reply_markup=main_menu)
        await state.clear()

@dp.message(EditExpense.waiting_for_expense_id)
async def process_edit_expense_id(message: types.Message, state: FSMContext):
    if message.text.lower() in ["❌ batal", "cancel", "back", "kembali"]:
        await state.clear()
        return await message.answer("🚫 Proses dibatalkan.", reply_markup=main_menu)
    try:
        expense_id = int(message.text)
        await state.update_data(expense_id=expense_id)
        await state.set_state(EditExpense.waiting_for_new_value)
        await message.answer("Masukkan nilai baru untuk pengeluaran:")
    except ValueError:
        await message.answer("Input tidak valid. Masukkan angka untuk ID pengeluaran.")

@dp.message(EditExpense.waiting_for_new_value)
async def process_edit_expense_new_value(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        expense_id = data.get("expense_id")
        new_value = float(message.text)
        db = SessionLocal()
        from app.crud import edit_expense_record
        success = edit_expense_record(db, expense_id, message.from_user.id, new_value)
        db.close()
        if success:
            await message.answer("Pengeluaran berhasil diperbarui.", reply_markup=main_menu)
        else:
            await message.answer("Gagal memperbarui pengeluaran. Pastikan ID pengeluaran benar.", reply_markup=main_menu)
    except ValueError:
        await message.answer("Input tidak valid. Masukkan angka untuk nilai baru.")
    except Exception as e:
        await message.answer(f"Terjadi kesalahan: {str(e)}")
    finally:
        await state.clear()

# --- Handler Default untuk Input yang Tidak Dikenali ---
@dp.message()
async def default_handler(message: types.Message):
    await message.answer("Maaf, perintah tidak dikenali. Silakan gunakan menu yang tersedia.", reply_markup=main_menu)

# --- Fungsi Utama untuk Menjalankan Bot ---
async def main():
    """Fungsi utama untuk menjalankan polling bot Telegram."""
    await dp.start_polling(bot)
