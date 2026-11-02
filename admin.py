import logging

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from config import PRIVATE_CHANNEL_ID, ADMIN_IDS
import storage

router = Router()
logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    return not ADMIN_IDS or user_id in ADMIN_IDS


@router.callback_query(F.data.startswith("mod:"))
async def process_moderation(callback: CallbackQuery, bot: Bot):
    if not _is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав на это действие.", show_alert=True)
        return

    _, action, app_id_str = callback.data.split(":")
    app_id = int(app_id_str)

    app = await storage.get_application(app_id)
    if not app:
        await callback.answer("Заявка не найдена.", show_alert=True)
        return

    if app["status"] != "pending":
        await callback.answer("Заявка уже обработана.", show_alert=True)
        return

    applicant_id = app["user_id"]

    if action == "accept":
        try:
            invite_link = await bot.create_chat_invite_link(
                chat_id=PRIVATE_CHANNEL_ID,
                member_limit=1,
                name=f"Заявка №{app_id}",
            )
        except Exception:
            logger.exception("Не удалось создать ссылку для заявки %s", app_id)
            await callback.answer(
                "Не удалось создать ссылку. Проверьте права бота в закрытом канале.",
                show_alert=True,
            )
            return

        try:
            await bot.send_message(
                applicant_id,
                "🎉 Ваша заявка одобрена!\n\n"
                f"Ваша одноразовая ссылка на закрытый канал:\n{invite_link.invite_link}",
            )
        except Exception:
            logger.warning("Не удалось написать пользователю %s", applicant_id)

        await storage.set_application_status(app_id, "accepted")
        status_text = "✅ ОДОБРЕНО"

    elif action == "decline":
        await storage.set_application_status(app_id, "declined")
        try:
            await bot.send_message(applicant_id, "😔 Ваша заявка отклонена.")
        except Exception:
            logger.warning("Не удалось написать пользователю %s", applicant_id)
        status_text = "❌ ОТКЛОНЕНО"

    elif action == "block":
        await storage.block_user(applicant_id)
        await storage.set_application_status(app_id, "blocked")
        status_text = "🚫 ЗАБЛОКИРОВАН"

    else:
        await callback.answer("Неизвестное действие.", show_alert=True)
        return

    new_caption = (
        f"{callback.message.caption}\n\n"
        f"{status_text} (админ: {callback.from_user.full_name})"
    )
    await callback.message.edit_caption(caption=new_caption, reply_markup=None)
    await callback.answer()
