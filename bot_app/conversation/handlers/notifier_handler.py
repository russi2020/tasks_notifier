import logging
import logging.config
from os import path

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext

from bot_app.conversation.handlers.common_functions import set_or_update_config
from bot_app.dialogs.buttons import PlanningButtons, NotifierButtons, DbButtons, confirm_or_not_confirm_kb
from bot_app.dialogs.dialogs import buttons_names, buttons_callbacks, msg, confirmation_callbacks
from bot_app.states.insert_results_state import InsertResultState
from bot_app.states.notifier_states import NotifierStates
from db.db_data_handler import DbDataHandler
from db.db_functions import DbFunctions
from redis_repository.redis_cache import cache


def init_notifier_handler(dp: Dispatcher, db: DbFunctions, db_buttons: DbButtons,
                          db_data_handler: DbDataHandler):
    log_file_path = path.join(path.dirname(path.abspath("__file__")), 'logging.ini')
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.info("Start tasks notifier handler")

    @dp.message_handler(lambda m: m.text == buttons_names.back_to_menu, state="*")
    async def go_to_main_menu(message: types.Message, state: FSMContext):
        await state.reset_state()
        await message.answer(msg.back_to_menu_text,
                             reply_markup=PlanningButtons.main_kb())

    @dp.message_handler(lambda m: m.text == buttons_names.notifier_functionality, state="*")
    async def start_notifier_handler(message: types.Message, state: FSMContext):
        await state.reset_state()
        await message.bot.send_message(chat_id=message.chat.id,
                                       text=msg.back_to_menu_text,
                                       reply_markup=PlanningButtons.back_to_menu())
        await message.answer(text=msg.notifier_message, reply_markup=NotifierButtons.notifier_kb())
        cache.setex(f"last_msg_{message.from_user.id}", 60 * 60 * 24,
                    message.message_id+3)
        await NotifierStates.notifier_state.set()

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.activate_aims,
                               state=NotifierStates.notifier_state)
    async def activate_aims(callback: types.CallbackQuery):
        await callback.message.answer(text=msg.notifier_choose_aim_to_activate,
                                      reply_markup=db_buttons.get_active_or_not_active_aims_names_kb(
                                          active=False)
                                      )

    @dp.callback_query_handler(lambda c: c.data.startswith("edit_config"),
                               state=NotifierStates.notifier_state)
    async def update_notifier_active_aims(callback: types.CallbackQuery):
        await set_or_update_config(dp=dp, db_function=db_buttons.get_active_or_not_active_aims_names_kb,
                                   callback=callback, text=msg.notifier_choose_aim_to_activate, active=False)

    @dp.callback_query_handler(lambda c: c.data.startswith("aim_name"), state=NotifierStates.notifier_state)
    async def update_aim_status(callback: types.CallbackQuery, state: FSMContext):
        aim_id = int(callback.data.split("#")[-1])
        async with state.proxy() as data:
            data["aim_id"] = aim_id
        aim_name = db.set_aim_status_active(aim_id)
        await callback.message.bot.send_message(chat_id=callback.message.chat.id,
                                                text=f"Статус цели '{aim_name}' изменен на активный. "
                                                     f"Вы будете получать уведомления по этой цели.")
        await callback.message.answer(text=msg.notifier_update_task_msg,
                                      reply_markup=db_buttons.get_tasks_names_kb(aim_id=aim_id))

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.active_aims_list, state="*")
    async def get_active_aims_list(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await callback.message.bot.send_message(chat_id=callback.message.chat.id,
                                                text=msg.back_to_menu_text,
                                                reply_markup=PlanningButtons.back_to_menu())
        await callback.message.answer(text=msg.notifier_active_aim_msg,
                                      reply_markup=NotifierButtons.active_aims_kb())
        await NotifierStates.notifier_state.set()

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.notifier_active_aims,
                               state=NotifierStates.notifier_state)
    async def get_active_tasks_list(callback: types.CallbackQuery):
        await callback.message.bot.send_message(chat_id=callback.message.chat.id,
                                                text=msg.notifier_active_aims_list)
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
        db.set_task_status(task_id=task_id, active=True)
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

    async def active_task_aim_choose(callback: types.CallbackQuery, text: str):
        aim_id = int(callback.data.split("#")[-1])
        await callback.message.answer(text=text,
                                      reply_markup=db_buttons.get_active_and_not_active_tasks_names_kb(
                                          aim_id=aim_id, active=True)
                                      )

    @dp.callback_query_handler(lambda c: c.data.startswith("aim_name"),
                               state=NotifierStates.notifier_state_disable_tasks)
    async def disable_active_task_aim_choose(callback: types.CallbackQuery):
        await active_task_aim_choose(callback=callback, text=msg.notifier_disable_active_task)

    @dp.callback_query_handler(lambda c: c.data.startswith("task_name_activate"),
                               state=NotifierStates.notifier_state_disable_tasks)
    async def disable_active_task(callback: types.CallbackQuery):
        task_id = int(callback.data.split("#")[-1])
        db.set_task_status(task_id=task_id, active=False)
        await dp.bot.send_message(chat_id=callback.message.chat.id,
                                  text=msg.notifier_task_become_disable)

    @dp.callback_query_handler(lambda c: c.data == buttons_callbacks.active_tasks,
                               state=NotifierStates.notifier_state)
    async def start_get_active_tasks(callback: types.CallbackQuery):
        await dp.bot.send_message(chat_id=callback.message.chat.id,
                                  text=db_data_handler.get_active_tasks_string())

    @dp.message_handler(lambda m: m.text == buttons_names.insert_task_results, state="*")
    async def start_insert_task_results(message: types.Message):
        await dp.bot.send_message(chat_id=message.chat.id, text=msg.tasks_back_to_menu,
                                  reply_markup=PlanningButtons.back_to_menu())
        await message.answer(text=msg.insert_results_start, reply_markup=db_buttons.get_active_aims_names_kb())
        await InsertResultState.insert_results_state.set()

    @dp.callback_query_handler(lambda c: c.data.startswith("active_aim_name"),
                               state=InsertResultState.insert_results_state)
    async def choose_task_to_insert_results(callback: types.CallbackQuery):
        await active_task_aim_choose(callback=callback, text=msg.insert_results_choose_task)

    @dp.callback_query_handler(lambda c: c.data.startswith("task_name_activate"),
                               state=InsertResultState.insert_results_state)
    async def get_task_id_for_active_task(callback: types.CallbackQuery, state: FSMContext):
        task_id = int(callback.data.split("#")[-1])
        async with state.proxy() as data:
            data["task_id"] = task_id
        await InsertResultState.next()
        await callback.message.answer(text=msg.insert_results_is_digit,
                                      reply_markup=confirm_or_not_confirm_kb(
                                          confirm=confirmation_callbacks.insert_task_digit_confirm,
                                          not_confirm=confirmation_callbacks.insert_task_digit_not_confirm
                                      ))

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.insert_task_digit_confirm,
                               state=InsertResultState.get_result_state)
    async def add_result_value(callback: types.CallbackQuery):
        await callback.message.answer(text=msg.insert_results_insert_result)

    @dp.message_handler(state=InsertResultState.get_result_state)
    async def write_result(message: types.Message, state: FSMContext):
        result_value = message.text
        if result_value.isdigit():
            async with state.proxy() as data:
                data["result"] = result_value
        else:
            await message.answer(text=msg.digit_error_message)
            return
        await InsertResultState.insert_info.set()
        await insert_result_active_task(message=message, state=state)

    @dp.message_handler(state=InsertResultState.insert_info)
    async def insert_result_active_task(message: types.Message, state: FSMContext):
        state_data = dict(await state.get_data())
        task_id = state_data.get("task_id")
        result = state_data.get("result")
        db.insert_result_for_active_task(task_id=task_id, result=result)
        db.insert_into_task_results_by_day(task_id=task_id, result=result)
        await dp.bot.send_message(chat_id=message.chat.id,
                                  text=msg.insert_results_success)
        check_task_complete = db_data_handler.check_status_for_complete(task_id=task_id)
        if check_task_complete:
            db_data_handler.close_completed_task(task_id=task_id)
            await message.answer(text=msg.insert_results_digit_task_complete,
                                 reply_markup=PlanningButtons.main_kb())
            await state.finish()
        else:
            await state.finish()

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.insert_task_digit_not_confirm,
                               state=InsertResultState.get_result_state)
    async def not_confirm_digit_to_insert(callback: types.CallbackQuery, state: FSMContext):
        state_data = dict(await state.get_data())
        task_id = state_data.get("task_id")
        check = db_data_handler.check_target_value_is_digit(task_id=task_id)
        if check:
            await dp.bot.send_message(chat_id=callback.message.chat.id,
                                      text=msg.insert_task_close_nd_task_error_msg)
            await start_insert_task_results(message=callback.message)
        else:
            await callback.message.answer(text=msg.insert_results_not_digit_msg,
                                          reply_markup=confirm_or_not_confirm_kb(
                                              confirm=confirmation_callbacks.insert_task_close_nd_task_confirm,
                                              not_confirm=confirmation_callbacks.insert_task_close_nd_task_not_confirm)
                                          )
            await InsertResultState.close_not_digit_task.set()

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.insert_task_close_nd_task_confirm,
                               state=InsertResultState.close_not_digit_task)
    async def close_not_digit_task(callback: types.CallbackQuery, state: FSMContext):
        state_data = dict(await state.get_data())
        task_id = state_data.get("task_id")
        db.update_deadline_date_end(task_id=task_id)
        db.insert_into_task_results_by_day(task_id=task_id)
        db.set_task_status(task_id=task_id, active=False)
        await dp.bot.send_message(chat_id=callback.message.chat.id, text=msg.insert_results_close_nd_task)
        await state.finish()
