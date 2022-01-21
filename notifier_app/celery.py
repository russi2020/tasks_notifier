from celery import Celery
from celery.schedules import crontab
from envparse import env

from notifier_app.celery_config import CeleryConfig


env.read_envfile()

redis_url = f"redis://{env.str('REDIS_HOST')}:{env.str('REDIS_PORT')}"
app = Celery('tasks', broker=redis_url)
app.config_from_object(CeleryConfig)

app.conf.beat_schedule = {
    "send_every_day_targets_notification": {
        "task": "notifier_app.tasks_notifier.send_target_by_day_message",
        "schedule": crontab(hour="*/8", minute="45", day_of_week="*")
    },
    "send_week_targets_notification": {
        "task": "notifier_app.tasks_notifier.send_target_by_week_message",
        "schedule": crontab(hour=9, minute=0, day_of_week="*")
    }
}
