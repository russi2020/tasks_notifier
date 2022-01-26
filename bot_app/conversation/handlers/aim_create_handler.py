import logging.config
import logging
from os import path

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext

from db.db_functions import DbFunctions
from db.db_data_handler import DbDataHandler

from bot_app.states.aims_states import AimsState
from bot_app.dialogs.dialogs import confirmation_callbacks, buttons_names, buttons_callbacks, msg
from bot_app.dialogs.buttons import confirm_or_not_confirm_kb, PlanningButtons, DbButtons


def init_aim_create_handler(dp: Dispatcher, db: DbFunctions, db_data_handler: DbDataHandler,
                            db_buttons: DbButtons):
    log_file_path = path.join(path.dirname(path.abspath("__file__")), 'logging.ini')
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.info("Start aim create handler")

    @dp.message_handler(lambda m: m.text == buttons_names.aims_functionality, state="*")
    async def handle_aims_functionality(message: types.Message, state: FSMContext):
        await state.finish()
        await message.bot.send_message(chat_id=message.chat.id,
                                       text=msg.back_to_menu_text,
                                       reply_markup=PlanningButtons.back_to_menu())
        await message.answer(msg.aims_choose_functionality,
                             reply_markup=PlanningButtons.aims_service_button())

    @dp.callback_query_handler(lambda c: c.data.startswith("aim_name"))
    async def get_tasks_by_aim_name(callback: types.CallbackQuery):
        aim_id = int(callback.data.split("#")[-1])
        tasks_by_aim_id_status = db_data_handler.get_tasks_status_string(aim_id)
        await callback.message.answer(tasks_by_aim_id_status)

    @dp.callback_query_handler(lambda c: c.data == "make_aims")
    async def start_aim_insert(callback: types.CallbackQuery):
        await callback.message.answer(msg.aims_write_aim, reply_markup=PlanningButtons.back_to_menu())
        await AimsState.create_aims.set()

    @dp.message_handler(lambda m: m.text == buttons_names.back_to_menu, state="*")
    async def go_to_main_menu(message: types.Message, state: FSMContext):
        if message.text == buttons_names.back_to_menu:
            await message.answer(msg.aims_choose_category,
                                 reply_markup=PlanningButtons.main_kb())
            await state.finish()
            return

    @dp.message_handler(state=AimsState.create_aims)
    async def insert_aim_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["aim_name"] = message.text
            await message.answer(
                text=f"Вы внесли цель {data['aim_name']}. Все верно внесено?",
                reply_markup=confirm_or_not_confirm_kb(
                    confirm=confirmation_callbacks.confirm_aim,
                    not_confirm=confirmation_callbacks.not_confirm_aim
                )
            )

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.confirm_aim,
                               state=AimsState.create_aims)
    async def confirmed_aim(callback: types.CallbackQuery, state: FSMContext):
        state_data = dict(await state.get_data())
        aim_name = state_data.get("aim_name")
        db.insert_aim(aim_name)
        await callback.message.answer(msg.aims_added_ti_db, reply_markup=PlanningButtons.main_kb())
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.not_confirm_aim,
                               state=AimsState.create_aims)
    async def not_confirmed_aim(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await start_aim_insert(callback)

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.aims_status, state="*")
    async def get_aims_status(callback: types.CallbackQuery):
        aims_status = db_data_handler.get_aims_status_string()
        await callback.message.answer(text=aims_status, reply_markup=PlanningButtons.main_kb())

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.tasks_by_aims_list, state="*")
    async def choose_aim(callback: types.CallbackQuery):
        await callback.message.answer(text=msg.tasks_choose_aim,
                                      reply_markup=db_buttons.get_aims_names_kb())

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.aim_name)
    async def get_tasks_by_aim(callback: types.CallbackQuery):
        aim_id = int(callback.data.split("#")[-1])
        tasks_info = db_data_handler.get_tasks_status_string(aim_id=aim_id)
        await callback.message.answer(
            text=tasks_info
        )
