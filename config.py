from kombu import Exchange, Queue

RMQHOST = "127.0.0.1"
RMQUSERNAME = "guest"
RMQPASSWORD = "guest"
RMQPORT = 5672
RMQVHOST = "/"

# set the following Celery object configuration settings
# WAG: the above definitions do not map to the Celery config dictionary fields

# redundant since this is equivalent to the default broker ...
# but we need that since there is no default results backend ...
BROKER_URL = 'amqp://%s:%s@%s:%i' % (RMQUSERNAME, RMQPASSWORD, RMQHOST, RMQPORT)
CELERY_RESULT_BACKEND = BROKER_URL

CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_IMPORTS = ['producer',]
CELERY_QUEUES = (
    Queue('celery', Exchange('celery'), routing_key='celery', queue_arguments={'x-max-priority': 10}),
)
