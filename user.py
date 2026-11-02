import logging

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import ADMIN_CHANNEL_ID, GOALS, GOAL_OTHER
from keyboards import (
    games_keyboard,
    videos_per_day_keyboard,
    goals_keyboard,
    moderation_keyboard,
)
from states import ApplicationForm
import storage

router = Router()
logger = logging.getLogger(__name__)

VIDEOS_INVALID_TEXT = "Введите число или выберите из меню"


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if await storage.is_blocked(message.from_user.id):
        await message.answer("Вы заблокированы и не можете подавать заявки.")
        return

    await state.clear()
    await message.answer(
        "Привет! Заполните анкету, чтобы подать заявку.\n\n1️⃣ Выберите игру:",
        reply_markup=games_keyboard(),
    )
    await state.set_state(ApplicationForm.choosing_game)


@router.callback_query(ApplicationForm.choosing_game, F.data.startswith("game:"))
async def process_game(callback: CallbackQuery, state: FSMContext):
    game = callback.data.split(":", 1)[1]
    await state.update_data(game=game)

    await callback.message.edit_text(f"1️⃣ Игра: {game} ✅")
    await callback.message.answer("2️⃣ Сколько у вас подписчиков в TikTok/YouTube?")
    await state.set_state(ApplicationForm.entering_subscribers)
    await callback.answer()


@router.message(ApplicationForm.entering_subscribers, F.text)
async def process_subscribers(message: Message, state: FSMContext):
    await state.update_data(subscribers=message.text.strip())
    await message.answer(
        "3️⃣ Сколько планируете выкладывать видео-роликов в день?\n"
        "Введите число или выберите вариант из меню:",
        reply_markup=videos_per_day_keyboard(),
    )
    await state.set_state(ApplicationForm.entering_videos_per_day)


@router.message(ApplicationForm.entering_subscribers)
async def process_subscribers_invalid(message: Message):
    await message.answer("Пожалуйста, напишите количество подписчиков текстом.")


@router.callback_query(
    ApplicationForm.entering_videos_per_day, F.data.startswith("videos:")
)
async def process_videos_callback(callback: CallbackQuery, state: FSMContext):
    option = callback.data.split(":", 1)[1]
    await state.update_data(videos_per_day=option)
    await callback.message.edit_text(f"3️⃣ Видео в день: {option} ✅")
    await ask_goal(callback.message, state)
    await callback.answer()


@router.message(ApplicationForm.entering_videos_per_day, F.text)
async def process_videos_text(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.isdigit():
        await state.update_data(videos_per_day=text)
        await ask_goal(message, state)
    else:
        await message.answer(VIDEOS_INVALID_TEXT, reply_markup=videos_per_day_keyboard())


@router.message(ApplicationForm.entering_videos_per_day)
async def process_videos_invalid(message: Message):
    await message.answer(VIDEOS_INVALID_TEXT, reply_markup=videos_per_day_keyboard())


async def ask_goal(message: Message, state: FSMContext):
    await message.answer("4️⃣ Какова ваша цель?", reply_markup=goals_keyboard())
    await state.set_state(ApplicationForm.choosing_goal)


@router.callback_query(ApplicationForm.choosing_goal, F.data.startswith("goal:"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split(":", 1)[1])
    goal_text = GOALS[index]

    if goal_text == GOAL_OTHER:
        await callback.message.edit_text(f"4️⃣ Цель: {GOAL_OTHER}")
        await callback.message.answer("Напишите своё:")
        await state.set_state(ApplicationForm.entering_custom_goal)
    else:
        await state.update_data(goal=goal_text)
        await callback.message.edit_text(f"4️⃣ Цель: {goal_text} ✅")
        await ask_screenshot(callback.message, state)

    await callback.answer()


@router.message(ApplicationForm.entering_custom_goal, F.text)
async def process_custom_goal(message: Message, state: FSMContext):
    await state.update_data(goal=message.text.strip())
    await ask_screenshot(message, state)


@router.message(ApplicationForm.entering_custom_goal)
async def process_custom_goal_invalid(message: Message):
    await message.answer("Пожалуйста, напишите текстом.")


async def ask_screenshot(message: Message, state: FSMContext):
    await message.answer(
        "5️⃣ Пришлите скриншот вашего аккаунта в TikTok/YouTube, на котором вы "
        "будете постить наши готовые видеоролики.\n\n"
        "⚠️ На скриншоте должно быть видно количество подписчиков."
    )
    await state.set_state(ApplicationForm.uploading_screenshot)


@router.message(ApplicationForm.uploading_screenshot, F.photo)
async def process_screenshot(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    photo_file_id = message.photo[-1].file_id
    applicant = message.from_user

    app_data = {
        "user_id": applicant.id,
        "username": applicant.username,
        "full_name": applicant.full_name,
        "game": data["game"],
        "subscribers": data["subscribers"],
        "videos_per_day": data["videos_per_day"],
        "goal": data["goal"],
        "screenshot_file_id": photo_file_id,
    }

    app_id = await storage.save_application(app_data)

    caption = (
        f"📨 Новая заявка №{app_id}\n\n"
        f"👤 Пользователь: {applicant.full_name} "
        f"(@{applicant.username or 'нет'}, id: {applicant.id})\n"
        f"🎮 Игра: {app_data['game']}\n"
        f"👥 Подписчиков: {app_data['subscribers']}\n"
        f"🎥 Видео в день: {app_data['videos_per_day']}\n"
        f"🎯 Цель: {app_data['goal']}"
    )

    await bot.send_photo(
        chat_id=ADMIN_CHANNEL_ID,
        photo=photo_file_id,
        caption=caption,
        reply_markup=moderation_keyboard(app_id),
    )

    await message.answer("✅ Заявка отправлена! Ожидайте решения.")
    await state.clear()


@router.message(ApplicationForm.uploading_screenshot)
async def process_screenshot_invalid(message: Message):
    await message.answer("Пожалуйста, пришлите скриншот (фото) вашего аккаунта.")
