import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHECK_INTERVAL_MIN = int(os.getenv("CHECK_INTERVAL_MIN", "60"))
DB_PATH = os.getenv("DB_PATH", "prices.db")
