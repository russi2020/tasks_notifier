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
    notifier_message: str = "Выберите функционал для уведомлений. " \
                            "Если вы установите статус цели как активный, то для этой " \
                            "цели будут отправляться уведомления в телеграмм"
    activate_task_for_active_aim: str = "Выберите задачу для выполнения. После активации задачи " \
                                        "будут приходить уведомления по этой задаче."
    notifier_choose_aim_for_task_activate: str = "Выберите цель для активации задач"
    notifier_aim_status_to_active: str = "Статус задачи изменен на 'активная'. По ней будут приходить "\
                                         "уведомления о статусе задачи"
    notifier_disable_active_aim: str = "Выберите цель отмены статуса 'активная'. Задачи по этой " \
                                       "цели также изменят статус на 'не активный'. Уведомления " \
                                       "больше не будут приходить."
    notifier_disable_active_task: str = "Выберите задачу для отмены статуса 'активная'. Уведомления " \
                                       "больше не будут приходить."
    notifier_aim_become_disables: str = "Статус цели изменен на неактивный. Уведомления больше не "\
                                       "будут отправляться"
    notifier_tasks_by_aim_disables: str = "Статус задач для цели изменен на неактивный. Уведомления "\
                                       "больше не будут отправляться для этих задач."
    notifier_task_disable_choose_aim: str = "Выберите цель, к которой привязана активная задача"
    notifier_task_become_disable: str = "Статус задачи изменен на неактивный. Уведомления больше не "\
                                       "будут отправляться"


@dataclass(frozen=True)
class ButtonNames:
    aims_functionality: str = "Планирование целей"
    tasks_functionality: str = "Планирование задач"
    statistics_functionality: str = "Статус выполнения целей и задач"
    notifier_functionality: str = "Уведомления по целям и задачам"
    aims_status : str = "Статус исполнения целей"
    tasks_status: str = "Статус исполнения задач"
    back_to_menu: str = "Вернуться в меню"
    notifier_activate_aims: str = "Установить активный статус для целей"
    notifier_active_aims_list: str = "Список активных целей"
    notifier_active_tasks: str = "Список активных задач"
    notifier_disable_active_aims: str = "Убрать цель из активных"
    notifier_disable_active_tasks: str = "Убрать задачу из активных"
    notifier_active_aims: str = "Получить данные об актиных целях"
    notifier_add_active_task_by_aim: str = "Добавить к активной цели новую задачу"


@dataclass(frozen=True)
class ButtonCallbacks:
    plans_on_year: str = "plans_on_year"
    plans_on_half_year: str = "plans_on_half_year"
    plans_on_month: str = "plans_on_month"
    activate_aims: str = "activate_aims"
    active_tasks: str = "active_tasks"
    active_aims_list: str = "active_aims"
    disable_active_aims: str = "disable_active_aims"
    disable_active_tasks: str = "disable_active_tasks"
    notifier_active_aims: str = "notifier_active_aims"
    notifier_add_active_task_by_aim: str = "notifier_add_active_task_by_aim"
    notifier_active_aim_to_update: str = "notifier_add_active_aim"


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
