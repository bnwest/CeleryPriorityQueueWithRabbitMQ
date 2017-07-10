import time

from consumer import APP

def spin(max):
    #start_time = datetime.now()
    k = 0
    for j in range(0,max):
        k = (k + j) % max
    #print k
    #stop_time = datetime.now()
    #print('elapsed time is {0}.'.format(stop_time - start_time))

COMPUTE_1_SECS  =  10123456
COMPUTE_2_SECS  =  20123456
COMPUTE_5_SECS  =  50123456
COMPUTE_10_SECS = 100123456
COMPUTE_20_SECS = 200123456

def compute(secs, cheat=False):
    for i in range(0,secs):
        spin(COMPUTE_1_SECS)
        if cheat:
            # force the context switch by sleeping
            time.sleep(0.05) # 50 milli-secs

@APP.task(queue='celery') # could add priority here
def do_stuff(priority):
    spin(COMPUTE_5_SECS) # time.sleep(5)
    #if priority == 9:
    #    time.sleep(150)
    return priority

@APP.task(queue='celery', priority=1)
def step1(name, priority=1):
    spin(COMPUTE_5_SECS) # time.sleep(5)
    return name

@APP.task(queue='celery', priority=3)
def step2(name, priority=2):
    spin(COMPUTE_20_SECS) # time.sleep(20)
    return name

@APP.task(queue='celery', priority=5)
def step3(name, priority=3):
    spin(COMPUTE_5_SECS) # time.sleep(5)
    return name

@APP.task(queue='celery', priority=7)
def step4(name, priority=4):
    spin(COMPUTE_2_SECS) # time.sleep(2)
    return name

@APP.task(queue='celery', priority=9)
def step5(name, priority=5):
    spin(COMPUTE_1_SECS) # time.sleep(1)
    return name

@APP.task(queue='celery')
def do_divide_by_zero(name, priority):
    x = 5
    y = x - 5
    z = x / y
    return name

@APP.task(queue='celery')
def do_timelimit_test(name, sleep_time):
    compute(sleep_time, cheat=True)
    # spin(sleep_time * COMPUTE_1_SECS)
    # time.sleep(sleep_time)
    return name
