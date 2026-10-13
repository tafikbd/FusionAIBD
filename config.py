import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

BKASH_NUMBER = os.getenv("BKASH_NUMBER", "01608364088")
ROCKET_NUMBER = os.getenv("ROCKET_NUMBER", "01608364088")
BINANCE_PAY_ID = os.getenv("BINANCE_PAY_ID", "1076189034")
USDT_TRC20 = os.getenv("USDT_TRC20", "TKeEd3wuTqHse2rdzAg3rqYeRfQD1NC7tq")
USDT_BSC20 = os.getenv("USDT_BSC20", "0xb83a03d9ded3ac7a4908aa87cfdfe1df9e05f719")

PLANS = {
    "free": {"name": "Free", "daily_limit": 20, "price_bdt": 0},
    "pro": {"name": "Pro", "daily_limit": 200, "price_bdt": 199},
    "premium": {"name": "Premium", "daily_limit": 99999, "price_bdt": 399},
    "lifetime": {"name": "Lifetime", "daily_limit": 99999, "price_bdt": 2999},
}

PRICING = {
    "pro": {"1m": {"days": 30, "price": 199, "label": "1 Month"}, "3m": {"days": 90, "price": 499, "label": "3 Months"}},
    "premium": {"1m": {"days": 30, "price": 399, "label": "1 Month"}, "3m": {"days": 90, "price": 999, "label": "3 Months"}},
    "lifetime": {"once": {"days": 36500, "price": 2999, "label": "One Time"}},
}

ANTI_SPAM_SECONDS = 5
FUSION_BADGE = (chr(10) + chr(10) + "---" + chr(10) + "Fusion AI BD - 3 AI in One" + chr(10) + "Groq + Gemini + DeepSeek")
