import os

# Все секреты и ID задаются через Railway → Variables или локальный .env.
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не задана обязательная переменная BOT_TOKEN")

def required_int(name: str) -> int:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Не задана обязательная переменная {name}")
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} должен быть целым числом") from exc

ADMIN_CHANNEL_ID = required_int("ADMIN_CHANNEL_ID")
PRIVATE_CHANNEL_ID = required_int("PRIVATE_CHANNEL_ID")

# Необязательно: Telegram user_id администраторов через запятую.
# Например: ADMIN_IDS=123456789,987654321
ADMIN_IDS = [
    int(value.strip())
    for value in os.getenv("ADMIN_IDS", "").split(",")
    if value.strip()
]

# Тексты и варианты анкеты
GAMES = ["Oxide"]
VIDEOS_PER_DAY_OPTIONS = ["1-2", "1-3", "1-5"]
GOAL_OTHER = "Другое"
GOALS = [
    "Помочь развитию канала",
    "Хочу попасть в тестеры платного чита",
    GOAL_OTHER,
]
