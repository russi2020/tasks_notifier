from aiogram.dispatcher.filters.state import StatesGroup, State


class StatisticState(StatesGroup):
    statistics_tasks_state = State()
