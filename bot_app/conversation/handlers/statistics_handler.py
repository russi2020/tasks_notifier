import logging

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext

from bot_app.dialogs.buttons import PlanningButtons, StatisticsButtons, DbButtons
from bot_app.dialogs.dialogs import buttons_names, msg, buttons_callbacks
from bot_app.states.statistic_states import StatisticState
from db.db_functions import DbFunctions
from db.db_data_handler import DbDataHandler


def init_statistics_handler(dp: Dispatcher, db_data_handler: DbDataHandler, db_buttons: DbButtons):
    logger = logging.getLogger(__name__)
    logger.info("Start statistics handler")

    @dp.message_handler(lambda m: m.text == buttons_names.statistics_functionality, state="*")
    async def handle_statistics_functionality(message: types.Message, state: FSMContext):
        await state.finish()
        await message.bot.send_message(chat_id=message.chat.id,
                                       text=msg.tasks_back_to_menu,
                                       reply_markup=PlanningButtons.back_to_menu())
        await message.answer("Выберите нужный функционал по статистике",
                             reply_markup=StatisticsButtons.aims_and_tasks_button())

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.statistics_aims_stats)
    async def handle_aims_status(callback: types.CallbackQuery):
        aims_status = db_data_handler.get_aims_status_string()
        await callback.message.bot.send_message(chat_id=callback.message.chat.id,
                                                text=msg.tasks_back_to_menu,
                                                reply_markup=PlanningButtons.back_to_menu())
        await callback.message.answer(aims_status, reply_markup=PlanningButtons.main_kb())

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.statistics_tasks_stats)
    async def handle_aims_status(callback: types.CallbackQuery):
        await callback.message.answer(text=msg.statistics_choose_aim,
                                      reply_markup=db_buttons.get_active_aims_names_kb())
        await StatisticState.statistics_tasks_state.set()

    @dp.callback_query_handler(lambda c: c.data.startswith("active_aim_name"),
                               state=StatisticState.statistics_tasks_state)
    async def add_active_task_for_active_aim(callback: types.CallbackQuery):
        aim_id = int(callback.data.split("#")[-1])
        tasks_status = db_data_handler.get_tasks_status_string(aim_id)
        await callback.message.answer(text=tasks_status)
