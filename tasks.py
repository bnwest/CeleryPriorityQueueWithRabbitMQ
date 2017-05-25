import time

from consumer import APP

@APP.task(queue='celery') # could add priority here
def do_stuff(priority):
    time.sleep(5)
    #if priority == 9:
    #    time.sleep(150)
    return priority

@APP.task(queue='celery', priority=1)
def step1(name, priority=1):
    time.sleep(5)
    return name

@APP.task(queue='celery', priority=3)
def step2(name, priority=2):
    time.sleep(20)
    return name

@APP.task(queue='celery', priority=5)
def step3(name, priority=3):
    time.sleep(5)
    return name

@APP.task(queue='celery', priority=7)
def step4(name, priority=4):
    time.sleep(2)
    return name

@APP.task(queue='celery', priority=9)
def step5(name, priority=5):
    time.sleep(1)
    return name

@APP.task(queue='celery', priority=10)
def do_divide_by_zero(name, priority):
    x = 5
    y = x - 5
    z = x / y
    return name

@APP.task(queue='celery', priority=10)
def do_timelimit_test(name, sleep_time):
    time.sleep(sleep_time)
    x = 5
    # return (x-5)/(x-5)
