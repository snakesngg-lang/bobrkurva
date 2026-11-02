from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import GAMES, VIDEOS_PER_DAY_OPTIONS, GOALS


def games_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for game in GAMES:
        builder.button(text=game, callback_data=f"game:{game}")
    builder.adjust(1)
    return builder.as_markup()


def videos_per_day_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for option in VIDEOS_PER_DAY_OPTIONS:
        builder.button(text=option, callback_data=f"videos:{option}")
    builder.adjust(3)
    return builder.as_markup()


def goals_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index, goal in enumerate(GOALS):
        builder.button(text=goal, callback_data=f"goal:{index}")
    builder.adjust(1)
    return builder.as_markup()


def moderation_keyboard(app_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Принять", callback_data=f"mod:accept:{app_id}")
    builder.button(text="❌ Отклонить", callback_data=f"mod:decline:{app_id}")
    builder.button(text="🚫 Заблокировать", callback_data=f"mod:block:{app_id}")
    builder.adjust(1)
    return builder.as_markup()
