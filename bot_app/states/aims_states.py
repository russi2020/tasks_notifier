from aiogram.dispatcher.filters.state import StatesGroup, State


class AimsState(StatesGroup):
    create_aims = State()
    statistics_by_aims = State()
