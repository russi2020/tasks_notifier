from envparse import env

env.read_envfile()


class CeleryConfig:
    broker_url = env.str("CELERY_BROKER_URL")
    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]
    timezone = env.str("TIME_ZONE")
    enable_utc = True
