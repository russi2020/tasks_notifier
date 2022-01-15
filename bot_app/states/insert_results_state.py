from aiogram.dispatcher.filters.state import StatesGroup, State


class InsertResultState(StatesGroup):
    insert_results_state = State()
    get_result_state = State()
    insert_info = State()
    close_not_digit_task = State()
