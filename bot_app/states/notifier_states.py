from aiogram.dispatcher.filters.state import StatesGroup, State


class NotifierStates(StatesGroup):
    notifier_state = State()
    notifier_state_disable_aims = State()
    notifier_state_disable_tasks = State()
