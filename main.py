# main.py
import sys
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
import uvicorn
from app.database import engine, Base
from app.routes import router
from app.bot import main as bot_main

app = FastAPI()

# Buat tabel database
Base.metadata.create_all(bind=engine)

# Register router API (opsional)
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    # Jalankan bot Telegram secara paralel dengan FastAPI
    asyncio.create_task(bot_main())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4587)
