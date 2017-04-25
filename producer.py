import time
from consumer import APP


@APP.task(queue='celery') # add priority= here
def do_stuff(priority):
    time.sleep(5)
    return priority

def run_priority_tasks():
    results = [ do_stuff.apply_async((pri,),  priority=pri) for pri in range (1,11) ]

    # no priority appears to have a lower priority than the lowest priority, for the win.
    # zero priority is an undocumented thing, which appears to be equivalent to no priority
    #results.append( do_stuff.apply_async((0,)            ) )
    #results.append( do_stuff.apply_async((1,), priority=1) )
    #results.append( do_stuff.apply_async((1,), priority=1) )
    #results.append( do_stuff.apply_async((99,), priority=0) )
    #results.append( do_stuff.apply_async((0,)            ) )

    return results


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
    time.sleep(10)
    return name

@APP.task(queue='celery', priority=9)
def step5(name, priority=5):
    time.sleep(5)
    return name

def do_multistep_job(name):
    result1 = step1.apply_async((name,1), priority=1)
    result1.wait()
    #time.sleep(3)
    result2 = step2.apply_async((name,3), priority=3)
    result2.wait()
    #time.sleep(3)
    result3 = step3.apply_async((name,5), priority=5)
    result3.wait()
    #time.sleep(3)
    result4 = step4.apply_async((name,7), priority=7)
    result4.wait()
    #time.sleep(3)
    result5 = step5.apply_async((name,9), priority=9)
    result5.wait()


#
# Prerequites:
#
# 1. RabbitMQ is installed and running with default settings:
#       $ rabbitmq-server
#       # cycle RabbitMQ:
#       $ rabbitmqctl stop_app; rabbitmqctl reset; rabbitmqctl start_app
#       # list queues
#       $ rabbitmqctl list_queues name messages consumers
#
# 2. Monitor RabbitMQ:
#       => http://localhost:15672/
#
# 3. Started the celery workers:
#       $ celery worker --app=consumer:APP -c 2 --loglevel=info
#       or $ celery multi start worker1 worker2 --app=consumer:APP -c 1 --loglevel=info
#          $ celery multi show  worker1 worker2 --app=consumer:APP -c 1 --loglevel=info
#          $ celery multi restart/stop worker1 worker2 --app=consumer:APP
#       # show workers statistics:
#       $ celery worker --app=consumer:APP inspect stats
#
# 4. Monitor celery:
#       $ flower --app=consumer:APP --port=5555 --broker_api=http://guest:guest@localhost:15672/api/
#       => http://localhost:5555/
#


import sys
if __name__ == '__main__':
    #import pdb
    #pdb.set_trace()
    
    # bash: (python producer.py job111 &) ; sleep 3 ; (python producer.py job222 &) ; sleep 3 ; (python producer.py job333 &) ; sleep 3 ; (python producer.py job444 &) ; sleep 3 ; (python producer.py job555 &)
    # csh: python producer.py job111 & ; sleep 3 ; python producer.py job222 & ; sleep 3 ; python producer.py job333 & ; sleep 3 ; python producer.py job444 & ; sleep 3 ; python producer.py job555 &
    job_name = sys.argv[1] if len(sys.argv) > 1 else 'job' 
    do_multistep_job(job_name)

    #results = run_priority_tasks()
    #num_results =len(results)
    #for result in results:
    #    result.wait()
    #    # side of the below access is that the result message is removed from the RabbitMQ broker
    #    print('id(%s) status(%s) result(%i)' % (result.id, result.status, result.result))

    