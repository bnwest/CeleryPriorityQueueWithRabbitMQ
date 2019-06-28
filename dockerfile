FROM python:2.7

RUN useradd celery -m -s /bin/bash

ADD requirements.txt /app/requirements.txt
ADD . /app/

WORKDIR /app/

RUN pip install -r requirements.txt

ENTRYPOINT celery -A consumer.APP worker --loglevel=info --uid=celery --gid=celery
#ENTRYPOINT ['celery','-A','consumer.AP', 'worker', '--loglevel=info', '--uid=celery', '--gid=celery']
