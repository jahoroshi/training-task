import os
import sys

from dotenv import load_dotenv
from celery import Celery


load_dotenv()
celery_app = Celery(__name__)
celery_app.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery_app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")

celery_app.conf.update(
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

celery_app.autodiscover_tasks(['src.tasks.worker'])
