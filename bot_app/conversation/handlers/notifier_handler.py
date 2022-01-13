import logging

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext

from bot_app.dialogs.buttons import PlanningButtons, NotifierButtons, DbButtons
from bot_app.dialogs.dialogs import buttons_names, buttons_callbacks, msg
from bot_app.states.notifier_states import NotifierStates
from db.db_functions import DbFunctions
from db.db_data_handler import DbDataHandler


def init_notifier_handler(dp: Dispatcher, db: DbFunctions, db_buttons: DbButtons,
                          db_data_handler: DbDataHandler):
    logger = logging.getLogger(__name__)
    logger.info("Start tasks notifier handler")

    @dp.message_handler(lambda m: m.text == buttons_names.back_to_menu, state="*")
    async def go_to_main_menu(message: types.Message, state: FSMContext):
        if message.text == buttons_names.back_to_menu:
            await message.answer("Открываю главное меню. Выберите категорию",
                                 reply_markup=PlanningButtons.main_kb())
            await state.finish()
            return

    @dp.message_handler(lambda m: m.text == buttons_names.notifier_functionality, state="*")
    async def start_notifier_handler(message: types.Message, state: FSMContext):
        await state.finish()
        await message.bot.send_message(chat_id=message.chat.id,
                                       text="Для возврата в меню нажмите кнопку ниже",
                                       reply_markup=PlanningButtons.back_to_menu())
        await message.answer(text=msg.notifier_message, reply_markup=NotifierButtons.notifier_kb())
        await NotifierStates.notifier_state.set()

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.activate_aims,
                               state=NotifierStates.notifier_state)
    async def activate_aims(callback: types.CallbackQuery):
        await callback.message.answer(text="Выберите цель для активации",
                                      reply_markup=db_buttons.get_active_or_not_active_aims_names_kb(
                                          active=False)
                                      )

    @dp.callback_query_handler(lambda c: c.data.startswith("aim_name"), state=NotifierStates.notifier_state)
    async def update_aim_status(callback: types.CallbackQuery, state: FSMContext):
        aim_id = int(callback.data.split("#")[-1])
        async with state.proxy() as data:
            data["aim_id"] = aim_id
        aim_name = db.set_aim_status_active(aim_id)
        await callback.message.bot.send_message(chat_id=callback.message.chat.id,
                                                text=f"Статус цели '{aim_name}' изменен на активный. "
                                                     f"Вы будете получать уведомления по этой цели.")
        await callback.message.answer(text="Нужно изменить статус задачи на активный для выбранной цели",
                                      reply_markup=db_buttons.get_tasks_names_kb(aim_id=aim_id))

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.active_aims_list, state="*")
    async def get_active_aims_list(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await callback.message.bot.send_message(chat_id=callback.message.chat.id,
                                                text="Для возврата в меню нажмите кнопку ниже",
                                                reply_markup=PlanningButtons.back_to_menu())
        await callback.message.answer(text="Вы можете выбрать список активных целей или активировать "
                                           "новые задачи", reply_markup=NotifierButtons.active_aims_kb())
        await NotifierStates.notifier_state.set()

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.notifier_active_aims,
                               state=NotifierStates.notifier_state)
    async def get_active_tasks_list(callback: types.CallbackQuery):
        await callback.message.bot.send_message(chat_id=callback.message.chat.id,
                                                text="Список активных целей")
        await callback.message.bot.send_message(chat_id=callback.message.chat.id,
                                                text=db_data_handler.get_active_aims_string())

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.notifier_add_active_task_by_aim,
                               state=NotifierStates.notifier_state)
    async def get_active_aims_to_update_tasks(callback: types.CallbackQuery):
        await callback.message.answer(msg.notifier_choose_aim_for_task_activate,
                                      reply_markup=db_buttons.get_active_aims_names_kb())

    @dp.callback_query_handler(lambda c: c.data.startswith("active_aim_name"),
                               state=NotifierStates.notifier_state)
    async def add_active_task_for_active_aim(callback: types.CallbackQuery):
        aim_id = int(callback.data.split("#")[-1])
        await callback.message.answer(text=msg.activate_task_for_active_aim,
                                      reply_markup=db_buttons.get_active_and_not_active_tasks_names_kb(
                                          aim_id=aim_id, active=False))

    @dp.callback_query_handler(lambda c: c.data.startswith("task_name"),
                               state=NotifierStates.notifier_state)
    async def activate_task(callback: types.CallbackQuery, state: FSMContext):
        task_id = int(callback.data.split("#")[-1])
        db.set_task_status_active(task_id=task_id)
        await callback.bot.send_message(chat_id=callback.message.chat.id,
                                        text=msg.notifier_aim_status_to_active)
        await dp.bot.send_message(chat_id=callback.message.chat.id, text=msg.main,
                                  reply_markup=PlanningButtons.main_kb())
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.disable_active_aims,
                               state=NotifierStates.notifier_state)
    async def start_disable_active_aim(callback: types.CallbackQuery):
        await callback.message.answer(text=msg.notifier_disable_active_aim,
                                      reply_markup=db_buttons.get_active_or_not_active_aims_names_kb(
                                          active=True
                                      ))
        await NotifierStates.notifier_state_disable_aims.set()

    @dp.callback_query_handler(lambda c: c.data.startswith("aim_name"),
                               state=NotifierStates.notifier_state_disable_aims)
    async def disable_active_aim(callback: types.CallbackQuery):
        aim_id = int(callback.data.split("#")[-1])
        db.set_aim_status_not_active(aim_id=aim_id)
        await dp.bot.send_message(chat_id=callback.message.chat.id,
                                  text=msg.notifier_aim_become_disables)
        db.set_task_status_not_active_by_aim_id(aim_id=aim_id)
        await dp.bot.send_message(chat_id=callback.message.chat.id,
                                  text=msg.notifier_tasks_by_aim_disables)

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.disable_active_tasks,
                               state=NotifierStates.notifier_state)
    async def start_disable_active_task(callback: types.CallbackQuery):
        await callback.message.answer(text=msg.notifier_task_disable_choose_aim,
                                      reply_markup=db_buttons.get_active_or_not_active_aims_names_kb(
                                          active=True
                                      ))
        await NotifierStates.notifier_state_disable_tasks.set()

    @dp.callback_query_handler(lambda c: c.data.startswith("aim_name"),
                               state=NotifierStates.notifier_state_disable_tasks)
    async def disable_active_task_aim_choose(callback: types.CallbackQuery):
        aim_id = int(callback.data.split("#")[-1])
        await callback.message.answer(text=msg.notifier_disable_active_task,
                                      reply_markup=db_buttons.get_active_and_not_active_tasks_names_kb(
                                          aim_id=aim_id, active=True)
                                      )

    @dp.callback_query_handler(lambda c: c.data.startswith("task_name_activate"),
                               state=NotifierStates.notifier_state_disable_tasks)
    async def disable_active_task(callback: types.CallbackQuery):
        task_id = int(callback.data.split("#")[-1])
        db.set_task_status_not_active(task_id=task_id)
        await dp.bot.send_message(chat_id=callback.message.chat.id,
                                  text=msg.notifier_task_become_disable)

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.active_tasks,
                               state=NotifierStates.notifier_state)
    async def start_get_active_tasks(callback: types.CallbackQuery):
        await dp.bot.send_message(chat_id=callback.message.chat.id,
                                  text=db_data_handler.get_active_tasks_string())
