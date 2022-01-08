from dataclasses import dataclass


@dataclass(frozen=True)
class Messages:
    test: str = 'Привет, {name}!'
    help: str = 'Помощь'
    help_message: str = 'Данное приложение выполняет следующие команды: \n' \
                        '/start - Начало работы с ботом.'
    main: str = 'Что будем делать?'
    btn_back: str = '<- Назад'
    btn_forward: str = 'Вперед ->'
    write_email: str = 'Для авторизации напишите вашу корпоративную почту'
    authorization_success: str = "Добро пожаловать!"
    add_target_value_or_not: str = "Нужно добавить числовое значение для задачи? "\
                                   "Например, если нужно прочитать 500 страниц."
    deadline_message: str = "Укажите сроки выполнения задачи. "\
                            "Например, 1 год, 6 месяцев, 4 недели, 5 дней. "\
                            "Или можно внести deadline задачи в формате 31-12-2021. "\
                            "Вносить данные именно в таком формате. Иначе они не будут обработаны. "\
                            "Исчисляемые значения указывайте цифрами."


@dataclass(frozen=True)
class ButtonNames:
    aims_functionality: str = "Планирование целей"
    tasks_functionality: str = "Планирование задач"
    statistics_functionality: str = "Статус выполнения целей и задач"
    aims_status : str = "Статус исполнения целей"
    tasks_status: str = "Статус исполнения задач"
    back_to_menu: str = "Вернуться в меню"


@dataclass(frozen=True)
class ButtonCallbacks:
    plans_on_year: str = "plans_on_year"
    plans_on_half_year: str = "plans_on_half_year"
    plans_on_month: str = "plans_on_month"


@dataclass(frozen=True)
class ConfirmationCallbacks:
    email_confirm: str = "correct_email"
    email_not_confirm: str = "not_correct_email"
    confirm_aim: str = "correct_aim"
    not_confirm_aim: str = "not_correct_aim"
    confirm_task: str = "correct_task"
    not_confirm_task: str = "not_correct_task"
    confirm_description: str = "description_add"
    not_confirm_description: str = "description_not_add"
    tasks_confirm_target_value: str = "confirm_target_value"
    tasks_not_confirm_target_value: str = "not_confirm_target_value"


msg = Messages()
confirmation_callbacks = ConfirmationCallbacks()
buttons_callbacks = ButtonCallbacks()
buttons_names = ButtonNames()
