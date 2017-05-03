from celery import Celery
from kombu import Exchange, Queue

# this definition is executed first time module is imported or this file is executed as a script:
# https://docs.python.org/2/tutorial/modules.html
# "Each module has its own private symbol table, which is used as the global symbol table by all functions defined in the module."

APP = Celery('producer') # producer.py is where we have defined all of the APP.task()s

# sets APP's configuration from file, resetting any exisitng configurations
APP.config_from_object('config')   # sets APP._config_source as well

# above is a  short cut to the following:
#APP.conf.update(CELERY_ACKS_LATE=True)
#APP.conf.update(CELERYD_PREFETCH_MULTIPLIER=1)
#APP.conf.update(CELERY_QUEUES=(
#    Queue('celery', Exchange('celery'), routing_key='celery', queue_arguments={'x-max-priority': 10}),
#))
#APP.conf.update(CELERY_IMPORTS=['producer',])

if __name__ == '__main__':
    APP.start()
