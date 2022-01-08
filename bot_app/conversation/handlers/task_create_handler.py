import logging

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext

from db.db_functions import DbFunctions
from db.db_data_handler import DbDataHandler

from bot_app.states.tasks_states import TasksState
from bot_app.dialogs.dialogs import confirmation_callbacks, buttons_names, msg
from bot_app.dialogs.buttons import confirm_or_not_confirm_kb, DbButtons, PlanningButtons
from bot_app.tools.text_handler import UserTextParser
from bot_app.tools.text_handler_date_values import DateTextHandler


def init_task_create_handler(dp: Dispatcher,
                             db: DbFunctions,
                             db_data_handler: DbDataHandler,
                             db_buttons: DbButtons,
                             ut_parser: UserTextParser):
    logger = logging.getLogger(__name__)
    logger.info("Start tasks create handler")

    @dp.message_handler(lambda m: m.text == buttons_names.back_to_menu, state="*")
    async def go_to_main_menu(message: types.Message, state: FSMContext):
        if message.text == buttons_names.back_to_menu:
            await message.answer("Открываю главное меню. Выберите категорию",
                                 reply_markup=PlanningButtons.main_kb())
            await state.finish()
            return

    @dp.message_handler(lambda m: m.text == buttons_names.tasks_functionality, state="*")
    async def handle_aims_tasks(message: types.Message, state: FSMContext):
        await state.finish()
        await message.bot.send_message(chat_id=message.chat.id,
                                       text="Для возврата в меню нажмите кнопку ниже",
                                       reply_markup=PlanningButtons.back_to_menu())
        await message.answer("Выберите цель, по которой надо посмореть задачи",
                             reply_markup=db_buttons.get_aims_names_kb())
        await TasksState.create_tasks.set()

    @dp.callback_query_handler(lambda c: c.data.startswith("aim_name"), state=TasksState.create_tasks)
    async def create_tasks(callback: types.CallbackQuery, state: FSMContext):
        aim_id = int(callback.data.split("#")[-1])
        async with state.proxy() as data:
            data['aim_id'] = aim_id
        await TasksState.next()
        await callback.message.answer("Напишите наименование задачи",
                                      reply_markup=PlanningButtons.back_to_menu())

    @dp.message_handler(state=TasksState.insert_task_name)
    async def insert_task_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["task_name"] = message.text
            await message.bot.send_message(chat_id=message.chat.id, text="Имя задачи внесено")
        await TasksState.next()
        await message.answer(
            "Нужно добавить описание задачи?",
            reply_markup=confirm_or_not_confirm_kb(
                confirm=confirmation_callbacks.confirm_description,
                not_confirm=confirmation_callbacks.not_confirm_description
            )
        )

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.confirm_description,
                               state=TasksState.insert_description)
    async def create_task_description(callback: types.CallbackQuery):
        await callback.message.answer("Опишите задачу. Ограничение 500 символов.")

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

    @dp.message_handler(lambda m: m.text == "Описание добавлено", state=TasksState.insert_description)
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
                                                text="Укажите числовое значение для задачи. "
                                                     "Например, 500. Указать нужно только число.")

    @dp.message_handler(state=TasksState.insert_target_value)
    async def insert_target_value(message: types.Message, state: FSMContext):
        target_value = message.text
        if target_value.isdigit():
            async with state.proxy() as data:
                data["target_value"] = target_value
        else:
            await message.answer(text="В ответе нужно указать только число! Например, 500.")
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
                                           text="Неверный формат даты. Введите заново.")
            await message.answer(msg.deadline_message)

    @dp.message_handler(state=TasksState.data_confirmation)
    async def task_info_confirmation(message: types.Message, state: FSMContext):
        state_data = dict(await state.get_data())
        task_name = state_data.get("task_name")
        task_description = state_data.get("task_description") if state_data.get(
            "task_description") else "Не внесено"
        task_deadline = state_data.get("task_deadline")
        await message.answer(
            text=f"Внесены следующие данные по задаче:\n"
                 f"Наименование задачи: {task_name}.\n"
                 f"Описание задачи: {task_description}\n"
                 f"Срок исполненения задачи: {task_deadline}\n"
                 f"Все верно внесено?",
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
                "task_description") else "Не внесено"
            aim_id = state_data.get("aim_id")
            target_value = int(state_data.get("target_value"))
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
                                await callback.message.answer("Неверный формат сообщения. "
                                                              "Введите информацию как в примере ниже.")
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
                await callback.message.answer("Неверный формат сообщения. "
                                              "Введите информацию как в примере ниже.")
                await create_task_deadline(callback, state)
            task_id = db.insert_task(task_name=task_name, description=task_description,
                                     aim_id=aim_id, target_value=target_value)
            deadline = info_to_db.get("deadline")
            if deadline:
                db.insert_deadline(deadline=deadline, task_id=task_id)
            else:
                await callback.message.answer("Неверный формат сообщения о deadline. "
                                              "Введите информацию как в примере ниже.")
                await create_task_deadline(callback, state)
            await callback.message.answer("Следующие данные внесены в базу данных в таблицу tasks:\n"
                                          f"Наименование задачи: {task_name}\n"
                                          f"Описание задачи: {task_description}\n"
                                          f"Целевой показатель: {target_value}\n")
            await callback.message.answer("В таблицу deadline внесены следующие данные:\n"
                                          f"Задача: {task_name}\n"
                                          f"Срок исполнения задачи: {deadline}\n")

            await callback.message.answer("Задача добавлена в базу данных")
            await state.finish()

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.not_confirm_task,
                               state=TasksState.data_confirmation)
    async def not_confirmed_task(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await TasksState.create_tasks.set()
        await handle_aims_tasks(callback.message, state)
