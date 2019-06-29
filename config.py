from kombu import Exchange, Queue

RMQHOST = "rabbitmq"
RMQUSERNAME = "guest"
RMQPASSWORD = "guest"
RMQPORT = 5672
RMQVHOST = "/"

# set the following Celery object configuration settings
# WAG: the above definitions do not map to the Celery config dictionary fields

# redundant since this is equivalent to the default broker ...
# but we need that since there is no default results backend ...
broker_url = 'amqp://%s:%s@%s:%i' % (RMQUSERNAME, RMQPASSWORD, RMQHOST, RMQPORT)
# result_backend = 'rpc://'
result_backend = 'redis://redis'

imports = ['producer',]
task_queues = (
    Queue('celery', Exchange('celery'), routing_key='celery', queue_arguments={'x-max-priority': 10}),
)

# If enabled task results will include the workers stack when re-raising task errors.
task_remote_tracebacks = True

# http://docs.celeryproject.org/en/latest/userguide/optimizing.html
# When using the default of early acknowledgment, having a prefetch multiplier setting of one,
# means the worker will reserve at most one extra task for every worker process: or in other words,
# if the worker is started with -c 10, the worker may reserve at most 20 tasks
# (10 unacknowledged tasks executing, and 10 unacknowledged reserved tasks) at any time.

# Only one Celery task at a time per worker
# =========================================

# How many messages to prefetch at a time multiplied by the number of concurrent processes.
# The default is 4 (four messages for each process).
# ... if the worker task runs a long time, you do not want one worker to sitting on 4 taks at a time
worker_prefetch_multiplier = 1

# Time (in seconds, or a timedelta object) for when after stored task tombstones will be deleted.
# ... for results backends when you are concerned that you will fill up the results backend
# in a 24 hr period (the default results expires value)
result_expires = 1 * 60 * 60 # aka 1 hour

# Maximum amount of resident memory, in kilobytes, that may be consumed by a worker
# before it will be replaced by a new worker.
# ... when celery workers get too big celery slows down
worker_max_memory_per_child = 4000000  # 4GB

# Maximum number of tasks a pool worker process can execute before it's replaced with a new one.
# ... draconian but ran into an example where a linked C library went sideways on an error
# and this was the work around
# worker_max_tasks_per_child = 1

# Task messages will be acknowledged after the task has been executed, not just before (the default behavior)
# Setting this to true allows the message to be re-queued, in the event of a power failure or
# the worker instance being killed abruptly, so this also means the task must be idempotent
# task_acks_late = True
# tasks that fail might get resubmitted ad infinitum

# Provide backwards Celery3 capatibility
# ======================================

task_serializer = "pickle"
result_serializer = "pickle"
accept_content = ["json", "pickle"]
