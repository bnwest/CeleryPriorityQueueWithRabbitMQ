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

# http://docs.celeryproject.org/en/latest/userguide/optimizing.html
# When using the default of early acknowledgment, having a prefetch multiplier setting of one,
# means the worker will reserve at most one extra task for every worker process: or in other words,
# if the worker is started with -c 10, the worker may reserve at most 20 tasks
# (10 unacknowledged tasks executing, and 10 unacknowledged reserved tasks) at any time.

# How many messages to prefetch at a time multiplied by the number of concurrent processes.
# The default is 4 (four messages for each process). 
CELERYD_PREFETCH_MULTIPLIER = 1

# Task messages will be acknowledged after the task has been executed, not just before (the default behavior)
# Setting this to true allows the message to be re-queued, in the event of a power failure or
# the worker instance being killed abruptly, so this also means the task must be idempotent
CELERY_ACKS_LATE = True

CELERY_IMPORTS = ['producer',]
CELERY_QUEUES = (
    Queue('celery', Exchange('celery'), routing_key='celery', queue_arguments={'x-max-priority': 10}),
)
