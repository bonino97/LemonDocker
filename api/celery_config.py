from celery import Celery  # type: ignore

celery = Celery('tasks', broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/0')

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

celery.autodiscover_tasks(['server'])

# Incluye directamente el módulo 'server' en lugar de autodiscovery

# celery.conf.update(
#     include=['server']
# )