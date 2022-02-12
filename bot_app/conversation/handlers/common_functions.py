from typing import Callable

from aiogram import types
from aiogram.dispatcher import Dispatcher

from redis_repository.redis_cache import cache


async def set_or_update_config(dp: Dispatcher, db_function: Callable, text: str,
                               callback: types.CallbackQuery = None,
                               user_id=None, page="", **kwargs):
    if callback is not None:
        user_id = callback.from_user.id
        page = callback.data.split("#")[-1]
    if page == "":
        await dp.bot.send_message(
            chat_id=callback.message.chat.id,
            text=text,
            reply_markup=db_function()
        )
    else:
        msg_id = cache.get(f"last_msg_{user_id}")
        await dp.bot.edit_message_reply_markup(
            user_id,
            message_id=msg_id,
            reply_markup=db_function(int(page), **kwargs)
        )
