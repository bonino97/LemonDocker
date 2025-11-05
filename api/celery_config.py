from celery import Celery  # type: ignore
import os

# Celery app configuration
celery = Celery(
    'lemondocker',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Enhanced configuration for parallel execution
celery.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task execution
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,

    # Worker configuration
    worker_prefetch_multiplier=1,  # Disable prefetching for better load distribution
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks to prevent memory leaks
    worker_disable_rate_limits=False,

    # Result backend
    result_expires=3600 * 24 * 7,  # Results expire after 7 days
    result_persistent=True,

    # Task time limits
    task_soft_time_limit=3600,  # 1 hour soft limit
    task_time_limit=7200,  # 2 hours hard limit

    # Retry policy
    task_default_retry_delay=60,  # Retry after 60 seconds
    task_max_retries=3,

    # Performance
    task_compression='gzip',
    result_compression='gzip',

    # Task routing
    task_routes={
        'server_v2.execute_pipeline': {'queue': 'pipelines'},
        'server_v2.execute_pipeline_step': {'queue': 'steps'},
    },

    # Include modules
    include=['server_v2', 'server']  # Include both v2 and legacy
)

# Beat schedule for periodic tasks (optional)
celery.conf.beat_schedule = {
    'cleanup-old-executions': {
        'task': 'server_v2.cleanup_executions',
        'schedule': 3600 * 24,  # Run daily
    },
}