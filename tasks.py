
from consumer import APP

def spin(max):
    k = 0
    for j in range(0,max):
        k = (k + j) % max

ONE_SEC = 10123456

def compute(secs, cheat=False):
    for i in range(0,secs):
        spin(ONE_SEC)
        if cheat:
            # force the context switch by sleeping
            time.sleep(0.05) # 50 milli-secs

@APP.task(queue='celery') # could add priority here
def do_stuff(priority):
    compute(5) # time.sleep(5)
    return priority

@APP.task(queue='celery', priority=1)
def step1(name, priority=1):
    compute(5) # time.sleep(5)
    return name

@APP.task(queue='celery', priority=3)
def step2(name, priority=2):
    compute(20) # time.sleep(20)
    return name

@APP.task(queue='celery', priority=5)
def step3(name, priority=3):
    compute(5) # time.sleep(5)
    return name

@APP.task(queue='celery', priority=7)
def step4(name, priority=4):
    compute(2) # time.sleep(2)
    return name

@APP.task(queue='celery', priority=9)
def step5(name, priority=5):
    compute(1) # time.sleep(1)
    return name

@APP.task(queue='celery')
def do_divide_by_zero(name, priority):
    x = 5
    y = x - 5
    z = x / y
    return name

@APP.task(queue='celery')
def do_timelimit_test(name, sleep_time):
    compute(sleep_time, cheat=False) # time.sleep(sleep_time)
    return name
