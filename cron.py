from app import app
from celery import Celery
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# For simplicity, MySQL is used as the broker for managing Celery task queues.
broker_url = app.config["CELERY_DATABASE_URI"]
result_backend = f"db+{app.config['SQLALCHEMY_DATABASE_URI']}"


def make_celery(app):
    # create context tasks in celery
    celery_instance = Celery(app.import_name, backend=result_backend, broker=broker_url)
    celery_instance.conf.update(
        CELERY_ENABLE_UTC=True,
        CELERY_TASK_RESULT_EXPIRES=18000,
        CELERY_RESULT_SERIALIZER="json",
        CELERY_RESULT_ENGINE_OPTIONS={"echo": True},
        CELERYBEAT_SCHEDULER="app.sinet.core.scheduler.DatabaseScheduler",
        CELERY_RESULT_DB_TABLENAMES={
            "task": "celery_result_taskmeta",
            "group": "celery_result_groupmeta",
        },
    )

    class ContextTask(celery_instance.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(self, *args, **kwargs)

    celery_instance.Task = ContextTask

    return celery_instance


celery = make_celery(app)
# celery worker -A cron.celery  -level=info -E
# celery worker -A cron.celery  -l info
# celery beat -A cron.celery  -l INFO
