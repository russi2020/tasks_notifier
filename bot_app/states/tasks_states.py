from aiogram.dispatcher.filters.state import StatesGroup, State


class TasksState(StatesGroup):
    create_aims = State()
    create_tasks = State()
    insert_task_name = State()
    insert_description = State()
    insert_target_value = State()
    insert_deadline = State()
    data_confirmation = State()
