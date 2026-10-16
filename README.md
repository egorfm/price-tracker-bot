# Price Tracker Bot

Telegram-бот, который следит за ценами на товары и пишет, когда цена падает.

## Возможности
- `/track <url>` — добавить товар
- `/list` — список отслеживаемых товаров
- `/untrack <id>` — удалить товар
- Фоновая проверка цен по расписанию (APScheduler)
- Парсинг цены через JSON-LD и meta-теги, без привязки к конкретному магазину

## Стек
Python 3.11+, aiogram 3, APScheduler, requests, BeautifulSoup, SQLite

## Запуск
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # вставь токен от @BotFather
python -m bot.main
```

## Тесты
```bash
pytest
```

## Ограничения и идеи
- Сайты с JS-рендерингом или защитой от ботов могут не отдавать цену
- TODO: CSS-селектор для конкретных магазинов, порог цены, Docker, график истории цен
