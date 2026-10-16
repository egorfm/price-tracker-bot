import asyncio
import logging

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot import db
from bot.config import BOT_TOKEN, CHECK_INTERVAL_MIN
from bot.handlers import router
from bot.scheduler import check_prices


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN:
        raise SystemExit("Set BOT_TOKEN in .env")

    db.init_db()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_prices, "interval", minutes=CHECK_INTERVAL_MIN, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
