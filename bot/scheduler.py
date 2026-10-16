import asyncio
import logging

from aiogram import Bot

from bot import db
from bot.parser import ParseError, fetch_product

log = logging.getLogger(__name__)


async def check_prices(bot: Bot) -> None:
    for item in db.all_items():
        try:
            _, price = await asyncio.to_thread(fetch_product, item["url"])
        except ParseError as e:
            log.warning("item %s: %s", item["id"], e)
            continue

        old = item["last_price"]
        if old is not None and price < old:
            await bot.send_message(
                item["user_id"],
                f"Цена упала!\n{item['title']}\n{old:g} → {price:g}\n{item['url']}",
            )
        if price != old:
            db.update_price(item["id"], price)
