import asyncio

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot import db
from bot.parser import ParseError, fetch_product

router = Router()


@router.message(Command("start", "help"))
async def cmd_start(message: Message):
    await message.answer(
        "Я слежу за ценами на товары.\n\n"
        "/track <ссылка> — начать отслеживание\n"
        "/list — мои товары\n"
        "/untrack <id> — перестать отслеживать"
    )


@router.message(Command("track"))
async def cmd_track(message: Message, command: CommandObject):
    url = (command.args or "").strip()
    if not url.startswith(("http://", "https://")):
        await message.answer("Использование: /track https://example.com/product")
        return
    await message.answer("Проверяю страницу...")
    try:
        title, price = await asyncio.to_thread(fetch_product, url)
    except ParseError as e:
        await message.answer(f"Ошибка: {e}")
        return
    if db.add_item(message.from_user.id, url, title, price):
        await message.answer(f"Отслеживаю: {title}\nТекущая цена: {price:g}")
    else:
        await message.answer("Этот товар уже в твоём списке.")


@router.message(Command("list"))
async def cmd_list(message: Message):
    items = db.list_items(message.from_user.id)
    if not items:
        await message.answer("Список пуст. Добавь товар через /track")
        return
    lines = [f"#{i['id']} {i['title']} — {i['last_price']:g}\n{i['url']}" for i in items]
    await message.answer("\n\n".join(lines), disable_web_page_preview=True)


@router.message(Command("untrack"))
async def cmd_untrack(message: Message, command: CommandObject):
    arg = (command.args or "").strip().lstrip("#")
    if not arg.isdigit():
        await message.answer("Использование: /untrack <id> (id смотри в /list)")
        return
    ok = db.remove_item(message.from_user.id, int(arg))
    await message.answer("Удалил." if ok else "Товар с таким id не найден.")
