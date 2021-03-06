import logging
import logging.config
from os import path

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext

from bot_app.conversation.handlers.common_functions import set_or_update_config
from bot_app.dialogs.buttons import confirm_or_not_confirm_kb, DbButtons, PlanningButtons
from bot_app.dialogs.dialogs import confirmation_callbacks, buttons_names, msg
from bot_app.states.tasks_states import TasksState
from bot_app.tools.text_handler import UserTextParser
from bot_app.tools.text_handler_date_values import DateTextHandler
from db.db_functions import DbFunctions
from redis_repository.redis_cache import cache


def init_task_create_handler(dp: Dispatcher,
                             db: DbFunctions,
                             db_buttons: DbButtons,
                             ut_parser: UserTextParser):
    log_file_path = path.join(path.dirname(path.abspath("__file__")), 'logging.ini')
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.info("Start tasks create handler")

    @dp.message_handler(lambda m: m.text == buttons_names.back_to_menu, state="*")
    async def go_to_main_menu(message: types.Message, state: FSMContext):
        await state.reset_state()
        await message.answer(msg.back_to_menu_text,
                             reply_markup=PlanningButtons.main_kb())

    @dp.message_handler(lambda m: m.text == buttons_names.tasks_functionality, state="*")
    async def handle_aims_tasks(message: types.Message, state: FSMContext):
        await state.reset_state()
        await message.bot.send_message(chat_id=message.chat.id,
                                       text=msg.tasks_back_to_menu,
                                       reply_markup=PlanningButtons.back_to_menu())
        await message.answer(msg.tasks_choose_aim,
                             reply_markup=db_buttons.get_aims_names_kb())
        cache.setex(f"last_msg_{message.from_user.id}", 60*60*24, message.message_id + 2)
        await TasksState.create_tasks.set()

    @dp.callback_query_handler(lambda c: c.data.startswith("edit_config"), state=TasksState.create_tasks)
    async def update_tasks_info(callback_query: types.CallbackQuery = None):
        await set_or_update_config(dp=dp, db_function=db_buttons.get_aims_names_kb,
                                   callback=callback_query, text=msg.tasks_choose_aim)

    @dp.callback_query_handler(lambda c: c.data.startswith("aim_name"), state=TasksState.create_tasks)
    async def create_tasks(callback: types.CallbackQuery, state: FSMContext):
        aim_id = int(callback.data.split("#")[-1])
        async with state.proxy() as data:
            data['aim_id'] = aim_id
        await TasksState.next()
        await callback.message.answer(msg.tasks_write_task_name,
                                      reply_markup=PlanningButtons.back_to_menu())

    @dp.message_handler(lambda m: m.text not in buttons_names.__dict__.values(),
                        state=TasksState.insert_task_name)
    async def insert_task_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["task_name"] = message.text
            await message.bot.send_message(chat_id=message.chat.id, text=msg.tasks_name_inserted)
        await TasksState.next()
        await message.answer(
            msg.tasks_need_add_description,
            reply_markup=confirm_or_not_confirm_kb(
                confirm=confirmation_callbacks.confirm_description,
                not_confirm=confirmation_callbacks.not_confirm_description
            )
        )

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.confirm_description,
                               state=TasksState.insert_description)
    async def create_task_description(callback: types.CallbackQuery):
        await callback.message.answer(msg.tasks_description_message)

    @dp.message_handler(state=TasksState.insert_description)
    async def insert_task_description(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["task_description"] = message.text
        await TasksState.next()
        await message.answer(
            text=msg.add_target_value_or_not,
            reply_markup=confirm_or_not_confirm_kb(
                confirm=confirmation_callbacks.tasks_confirm_target_value,
                not_confirm=confirmation_callbacks.tasks_not_confirm_target_value
            )
        )

    @dp.message_handler(lambda m: m.text == "???????????????? ??????????????????", state=TasksState.insert_description)
    async def target_value_confirm_or_not(message: types.Message):
        await TasksState.insert_target_value.set()
        await message.answer(
            text=msg.add_target_value_or_not,
            reply_markup=confirm_or_not_confirm_kb(
                confirm=confirmation_callbacks.tasks_confirm_target_value,
                not_confirm=confirmation_callbacks.tasks_not_confirm_target_value
            )
        )

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.not_confirm_description,
                               state=TasksState.insert_description)
    async def tasks_target_value_confirm_or_not(callback: types.CallbackQuery):
        await TasksState.next()
        message = callback.message
        await message.answer(
            text=msg.add_target_value_or_not,
            reply_markup=confirm_or_not_confirm_kb(
                confirm=confirmation_callbacks.tasks_confirm_target_value,
                not_confirm=confirmation_callbacks.tasks_not_confirm_target_value
            )
        )

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.tasks_confirm_target_value,
                               state=TasksState.insert_target_value)
    async def add_target_value(callback: types.CallbackQuery):
        await callback.message.bot.send_message(chat_id=callback.message.chat.id,
                                                text=msg.add_target_value_text)

    @dp.message_handler(state=TasksState.insert_target_value)
    async def insert_target_value(message: types.Message, state: FSMContext):
        target_value = message.text
        if target_value.isdigit():
            async with state.proxy() as data:
                data["target_value"] = target_value
        else:
            await message.answer(text=msg.digit_error_message)
            return
        await TasksState.next()
        await message.bot.send_message(chat_id=message.chat.id,
                                       text=msg.deadline_message)

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.tasks_not_confirm_target_value,
                               state=TasksState.insert_target_value)
    async def create_task_deadline(callback: types.CallbackQuery):
        await TasksState.insert_deadline.set()
        await callback.message.answer(msg.deadline_message)

    @dp.message_handler(state=TasksState.insert_deadline)
    async def insert_deadline(message: types.Message, state: FSMContext):
        if DateTextHandler.validate_user_text(text=message.text):
            async with state.proxy() as data:
                data["task_deadline"] = message.text
            await TasksState.next()
            await task_info_confirmation(message=message, state=state)
        else:
            await message.bot.send_message(chat_id=message.chat.id,
                                           text=msg.tasks_wrong_date_format)
            await message.answer(msg.deadline_message)

    @dp.message_handler(state=TasksState.data_confirmation)
    async def task_info_confirmation(message: types.Message, state: FSMContext):
        state_data = dict(await state.get_data())
        task_name = state_data.get("task_name")
        task_description = state_data.get("task_description") if state_data.get(
            "task_description") else None
        target_value = state_data.get("target_value") if state_data.get(
            "target_value") else 0
        task_deadline = state_data.get("task_deadline")
        await message.answer(
            text=f"?????????????? ?????????????????? ???????????? ???? ????????????:\n"
                 f"???????????????????????? ????????????: {task_name}.\n"
                 f"???????????????? ????????????: {task_description}\n"
                 f"?????????????? ????????????????????: {target_value}\n"
                 f"???????? ???????????????????????? ????????????: {task_deadline}\n"
                 f"?????? ?????????? ???????????????",
            reply_markup=confirm_or_not_confirm_kb(
                confirm=confirmation_callbacks.confirm_task,
                not_confirm=confirmation_callbacks.not_confirm_task
            )
        )

        @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.confirm_task,
                                   state=TasksState.data_confirmation)
        async def confirmed_task(callback: types.CallbackQuery, state: FSMContext):
            info_to_db = {}
            state_data = dict(await state.get_data())
            task_name = state_data.get("task_name")
            task_description = state_data.get("task_description") if state_data.get(
                "task_description") else "???? ??????????????"
            aim_id = state_data.get("aim_id")
            if state_data.get("target_value"):
                target_value = int(state_data.get("target_value"))
            else:
                target_value = None
            task_deadline = state_data.get("task_deadline")
            user_date_text = ut_parser.parse_text(task_deadline)
            print(f"user_date_text: {user_date_text}")
            if isinstance(user_date_text, list):
                parsed_value = ut_parser.get_parsed_values_list(user_date_text)
                if isinstance(parsed_value, list):
                    int_value, date_value = None, None
                    for i in parsed_value:
                        if i.isdigit():
                            int_value = int(i)
                        else:
                            value_date_type = DateTextHandler.convert_values_to_date_str_format(i)
                            if value_date_type:
                                date_value = value_date_type
                            else:
                                await callback.message.answer(msg.wrong_message_format)
                                await create_task_deadline(callback)
                    if int_value and date_value:
                        info_to_db["date_value"]: int = int_value
                        info_to_db["date_item_type"]: str = date_value
                else:
                    await callback.message.answer(parsed_value)
                    await create_task_deadline(callback)
            elif DateTextHandler.validate_user_text(user_date_text, user_date_text):
                date_for_db = DateTextHandler.get_date_type_for_db(user_date_text)
                info_to_db["deadline"] = date_for_db
            else:
                await callback.message.answer(msg.wrong_message_format)
                await create_task_deadline(callback, state)
            task_id = db.insert_task(task_name=task_name, description=task_description,
                                     aim_id=aim_id, target_value=target_value)
            deadline = info_to_db.get("deadline")
            if deadline:
                db.insert_deadline(deadline=deadline, task_id=task_id)
            else:
                await callback.message.answer(msg.wrong_message_format)
                await create_task_deadline(callback, state)
            await callback.message.answer("?????????????????? ???????????? ?????????????? ?? ???????? ???????????? ?? ?????????????? tasks:\n"
                                          f"???????????????????????? ????????????: {task_name}\n"
                                          f"???????????????? ????????????: {task_description}\n"
                                          f"?????????????? ????????????????????: {target_value}\n")
            await callback.message.answer("?? ?????????????? deadline ?????????????? ?????????????????? ????????????:\n"
                                          f"????????????: {task_name}\n"
                                          f"???????? ???????????????????? ????????????: {deadline}\n")

            await callback.message.answer("???????????? ?????????????????? ?? ???????? ????????????")
            await state.finish()

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.not_confirm_task,
                               state=TasksState.data_confirmation)
    async def not_confirmed_task(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await TasksState.create_tasks.set()
        await handle_aims_tasks(callback.message, state)
