from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from bot_app.dialogs.dialogs import buttons_callbacks, buttons_names
from db.db_functions import DbFunctions

BACK_TO_MENU_TEXT: str = 'Вернуться в меню'

BACK_TO_MENU_BUTTON = ReplyKeyboardMarkup(
    [[KeyboardButton(text=BACK_TO_MENU_TEXT)]], resize_keyboard=True)
REMOVE_INLINE_KEYBOARD_REPLY = InlineKeyboardMarkup(inline_keyboard=[])
SHARE_EMAIL = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Поделиться email')]])

# MAIN_KB = ReplyKeyboardMarkup(
#     resize_keyboard=True,
#     one_time_keyboard=True
# ).row(KeyboardButton(msg.services),
#       KeyboardButton(msg.help)
#       )


class DbButtons:

    def __init__(self, dbf: DbFunctions):
        self.db = dbf

    def get_aims_names_kb(self) -> InlineKeyboardMarkup:
        aims = self.db.get_all_aims_ids_and_names()
        kb = InlineKeyboardMarkup()
        for aim in aims:
            kb.add(
                InlineKeyboardButton(f"{aim[0]}. {aim[1]}", callback_data=f"aim_name#{aim[0]}"),
            )
        return kb

    def get_active_aims_names_kb(self) -> InlineKeyboardMarkup:
        active_aims = self.db.select_active_or_not_active_aims(active=True)
        kb = InlineKeyboardMarkup()
        for aim in active_aims:
            kb.add(
                InlineKeyboardButton(f"{aim[0]}. {aim[1]}", callback_data=f"active_aim_name#{aim[0]}"),
            )
        return kb

    def get_active_or_not_active_aims_names_kb(self, active: bool) -> InlineKeyboardMarkup:
        not_active_aims = self.db.select_active_or_not_active_aims(active=active)
        kb = InlineKeyboardMarkup()
        for aim in not_active_aims:
            kb.add(
                InlineKeyboardButton(f"{aim[0]}. {aim[1]}", callback_data=f"aim_name#{aim[0]}"),
            )
        return kb

    def get_tasks_names_kb(self, aim_id: int) -> InlineKeyboardMarkup:
        tasks = self.db.get_all_tasks_ids_and_names_by_aim_id(aim_id=aim_id)
        kb = InlineKeyboardMarkup()
        for task in tasks:
            kb.add(
                InlineKeyboardButton(f"{task[0]}. {task[1]}", callback_data=f"task_name#{task[0]}"),
            )
        return kb

    def get_active_and_not_active_tasks_names_kb(self, aim_id: int, active: bool) -> InlineKeyboardMarkup:
        tasks = self.db.select_active_or_not_active_tasks(aim_id=aim_id, active=active)
        kb = InlineKeyboardMarkup()
        for task in tasks:
            kb.add(
                InlineKeyboardButton(f"{task[0]}. {task[1]}", callback_data=f"task_name_activate#{task[0]}"),
            )
        return kb


def authorize() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('Авторизоваться', callback_data='authorize'))
    return kb


def confirm_or_not_confirm_kb(confirm: str, not_confirm: str) -> InlineKeyboardMarkup:
    """
    Подтверждаем или не подтверждаем введенные данные
    :return: InlineKeyboardMarkup
    """
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton('Да', callback_data=confirm),
        InlineKeyboardButton('Нет', callback_data=not_confirm)
    )
    return kb


class PlanningButtons:

    @staticmethod
    def main_kb() -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        kb.add(
            KeyboardButton(buttons_names.aims_functionality),
            KeyboardButton(buttons_names.tasks_functionality),
            KeyboardButton(buttons_names.statistics_functionality),
            KeyboardButton(buttons_names.notifier_functionality),
            KeyboardButton(buttons_names.insert_task_results),
        )
        return kb

    @staticmethod
    def back_to_menu() -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        kb.add(buttons_names.back_to_menu)
        return kb

    @staticmethod
    def statistics_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton(buttons_names.aims_status, callback_data="aims_status"),
            InlineKeyboardButton(buttons_names.tasks_status, callback_data="tasks_status")
        )
        return kb

    @staticmethod
    def aims_service_button() -> InlineKeyboardMarkup:
        """
        Просто кнопка для начала планирования.
        :return: InlineKeyboardMarkup
        """
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton("Запланировать цели", callback_data="make_aims"),
            InlineKeyboardButton("Посмотреть статус целей", callback_data="aims_status"),
            InlineKeyboardButton("Задачи относящиеся к цели", callback_data="aims_tasks")
        )
        return kb

    @staticmethod
    def start_tasks_button() -> InlineKeyboardMarkup:
        """
        Просто кнопка для начала планирования.
        :return: InlineKeyboardMarkup
        """
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("Запланировать задачи", callback_data="make_tasks"),
            InlineKeyboardButton("Посмотреть статус задач", callback_data="tasks_status"),
        )
        return kb

    @staticmethod
    def create_tasks_kb() -> InlineKeyboardMarkup:
        """Фишка планирования.
        1) Изначально выбираем цели на год. Указываем им наименования. Без числовых значений. Создается
        таблица с наименованиями целей на год.
        Затем в той же ветке по целям на год расписываем конеретные задачи с числовым значением на год.
        Создается таблица с конкретными задачвми под цели (Foreign Key на таблицу с целями для каждой задачи).
        2) Затем Если ставим цели на полгода, выкатывается список кнопок с написанными ранее целями, чтобы
        их можно было выбрать. Выбираются цели на полгода (равны сумма всех целей 1/2 не более на выбор).
        В таблице для целей на полгода создаются записи из таблицы целей на год (без числовых значений таблица).
        Далее выбираем задачи по каждой выбранной цели. Создается таблица с выбранными задачами.
        3) Далее цели на месяц. Также по сути как пункт 2 (только суммарно можно выбрать не более 1/3 от целей
        на полгода.
        """
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton('Запланировать задачи на год', callback_data=buttons_callbacks.plans_on_year),
            InlineKeyboardButton('Запланировать задачи на полгода', callback_data=buttons_callbacks.plans_on_half_year),
            InlineKeyboardButton('Запланировать задачи на 1 месяц', callback_data=buttons_callbacks.plans_on_month)
        )
        return kb

    @staticmethod
    def check_tasks_kb() -> InlineKeyboardMarkup:
        """Выводит список задач на год, полгода, месяц"""
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton('Список целей на год', callback_data='show_plans_on_year'),
            InlineKeyboardButton('Список целей на полгода', callback_data='show_plans_on_half_year'),
            InlineKeyboardButton('Список целей на 1 месяц', callback_data='show_plans_on_month')
        )
        return kb

    @staticmethod
    def send_results_by_day_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton('Получить список задач на день', callback_data='tasks_for_day_list'),
            InlineKeyboardButton('Отметить исполнение задач')
        )
        return kb

    @staticmethod
    def tasks_by_week_kb() -> InlineKeyboardMarkup:
        pass

    @staticmethod
    def tasks_by_day_kb() -> InlineKeyboardMarkup:
        """Список задач пункта 2 клавиатуры send_results_by_day_kb. Есть таблица задач по днем. С нее выборка.
        Нужна для заполнения данных по выполненным за день задачам
        """
        pass


class NotifierButtons:

    @staticmethod
    def notifier_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(buttons_names.notifier_activate_aims,
                                 callback_data=buttons_callbacks.activate_aims),
            InlineKeyboardButton(buttons_names.notifier_active_aims_list,
                                 callback_data=buttons_callbacks.active_aims_list),
            InlineKeyboardButton(buttons_names.notifier_active_tasks,
                                 callback_data=buttons_callbacks.active_tasks),
            InlineKeyboardButton(buttons_names.notifier_disable_active_aims,
                                 callback_data=buttons_callbacks.disable_active_aims),
            InlineKeyboardButton(buttons_names.notifier_disable_active_tasks,
                                 callback_data=buttons_callbacks.disable_active_tasks),
        )
        return kb

    @staticmethod
    def active_aims_kb():
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(buttons_names.notifier_active_aims_list,
                                 callback_data=buttons_callbacks.notifier_active_aims),
            InlineKeyboardButton(buttons_names.notifier_add_active_task_by_aim,
                                 callback_data=buttons_callbacks.notifier_add_active_task_by_aim)
        )
        return kb
