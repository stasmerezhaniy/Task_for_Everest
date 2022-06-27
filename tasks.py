from celery import Celery
from celery.result import AsyncResult
import time
import datetime


REDIS_URL = 'redis://redis:6379/0'
BROKER_URL = 'amqp://admin:mypass@rabbit//'

CELERY = Celery('tasks',
                backend=REDIS_URL,
                broker=BROKER_URL)

CELERY.conf.accept_content = ['json', 'msgpack']
CELERY.conf.result_serializer = 'msgpack'


def get_job(job_id):
    return AsyncResult(job_id, app=CELERY)


@CELERY.task()
def image_demension(img):
    time.sleep(60)
    location = datetime.datetime.now()
    print(location)

    return location
