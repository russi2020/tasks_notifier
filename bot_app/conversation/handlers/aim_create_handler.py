import logging

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext

from db.db_functions import DbFunctions
from db.db_data_handler import DbDataHandler

from bot_app.states.tasks_states import TasksState
from bot_app.dialogs.dialogs import confirmation_callbacks, buttons_names
from bot_app.dialogs.buttons import confirm_or_not_confirm_kb, PlanningButtons


def init_aim_create_handler(dp: Dispatcher, db: DbFunctions, db_data_handler: DbDataHandler):
    logger = logging.getLogger(__name__)
    logger.info("Start aim create handler")

    @dp.message_handler(lambda m: m.text == buttons_names.aims_functionality, state="*")
    async def handle_aims_functionality(message: types.Message, state: FSMContext):
        await state.finish()
        await message.bot.send_message(chat_id=message.chat.id,
                                       text="Для возврата в меню нажмите кнопку ниже",
                                       reply_markup=PlanningButtons.back_to_menu())
        await message.answer("Выберите нужный функционал по целям",
                             reply_markup=PlanningButtons.aims_service_button())

    @dp.message_handler(lambda m: m.text == buttons_names.statistics_functionality)
    async def handle_aims_status(message: types.Message):
        aims_status = db_data_handler.get_aims_status_string()
        await message.bot.send_message(chat_id=message.chat.id,
                                       text="Для возврата в меню нажмите кнопку ниже",
                                       reply_markup=PlanningButtons.back_to_menu())
        await message.answer(aims_status)

    @dp.callback_query_handler(lambda c: c.data.startswith("aim_name"))
    async def get_tasks_by_aim_name(callback: types.CallbackQuery):
        aim_id = int(callback.data.split("#")[-1])
        tasks_by_aim_id_status = db_data_handler.get_tasks_status_string(aim_id)
        await callback.message.answer(tasks_by_aim_id_status)

    @dp.callback_query_handler(lambda c: c.data == "make_aims")
    async def start_aim_insert(callback: types.CallbackQuery):
        await callback.message.answer("Напишите цель", reply_markup=PlanningButtons.back_to_menu())
        await TasksState.create_aims.set()

    @dp.message_handler(lambda m: m.text == buttons_names.back_to_menu, state="*")
    async def go_to_main_menu(message: types.Message, state: FSMContext):
        if message.text == buttons_names.back_to_menu:
            await message.answer("Открываю главное меню. Выберите категорию",
                                 reply_markup=PlanningButtons.main_kb())
            await state.finish()
            return

    @dp.message_handler(lambda m: m.text == "Напишите цель", state=TasksState.create_aims)
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
                               state=TasksState.create_aims)
    async def confirmed_aim(callback: types.CallbackQuery, state: FSMContext):
        state_data = dict(await state.get_data())
        aim_name = state_data.get("aim_name")
        db.insert_aim(aim_name)
        await callback.message.answer("Цель добавлена в базу данных", reply_markup=PlanningButtons.main_kb())
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.not_confirm_aim,
                               state=TasksState.create_aims)
    async def not_confirmed_aim(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await start_aim_insert(callback)
