from celery.beat import crontab

CELERYBEAT_SCHEDULE = {
    'update_db': {
        'task': 'manager.periodic_task',
        'schedule': crontab(minute='*'),
        'args': ()
    }
}
