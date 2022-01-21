import requests
from envparse import Env

from notifier_app.celery import app
from notifier_app.notifier_calculations import NotifierCalculations
from db.db_functions import DbFunctions

env = Env()
env.read_envfile()


db = DbFunctions()
notifier_calc = NotifierCalculations(db=db)
base_telegram_api_url = f"https://api.telegram.org/bot{env.str('TELEGRAM_TOKEN')}/"


def geturl_for_request(base_url: str, method: str, chat_id: str, text: str):
    full_url = base_url + method + f'?chat_id={chat_id}' + f'&text={text}'
    return full_url


def send_target(aim_id: int, task_id: int, value_to_divide: int):
    tv_message_by_day = notifier_calc.get_notification_to_send(
        aim_id=aim_id,
        task_id=task_id,
        value_to_divide=value_to_divide
    )
    telegram_ids_list = db.get_users_telegram_ids()
    for telegram_id in telegram_ids_list:
        full_url = geturl_for_request(base_url=base_telegram_api_url,
                                      method="sendmessage",
                                      chat_id=telegram_id[0], text=tv_message_by_day)
        with open('test.txt', 'w') as f:
            f.write(full_url)
        requests.post(url=full_url)


@app.task
def send_target_by_day_message():
    task_info = db.select_all_active_tasks_ids()
    for item in task_info:
        aim_id, task_id = item
        send_target(aim_id=aim_id, task_id=task_id, value_to_divide=1)


@app.task
def send_target_by_week_message():
    task_info = db.select_all_active_tasks_ids()
    for item in task_info:
        aim_id, task_id = item
        send_target(aim_id=aim_id, task_id=task_id, value_to_divide=7)
