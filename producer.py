import time

from celery.exceptions    import TimeoutError
from billiard.exceptions  import TimeLimitExceeded as Celery3_TimeLimitExceeded
from celery.exceptions    import TimeLimitExceeded as Celery4_TimeLimitExceeded

from consumer import APP
from tasks import *

from celery import signature, group

import pdb

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

def do_multistep_job(name):
    #pdb.set_trace()
    result1 = step1.apply_async((name,1), priority=1)
    result1.wait()
    #time.sleep(3)
    result2 = step2.apply_async((name,3), priority=3)
    result2.wait()
    #time.sleep(3)
    result3 = step3.apply_async((name,5), priority=5)
    result3.wait()
    #time.sleep(3)
    result41 = step4.apply_async((name,7), priority=7)
    result42 = step4.apply_async((name,7), priority=7)
    result43 = step4.apply_async((name,7), priority=7)
    result44 = step4.apply_async((name,7), priority=7)
    result45 = step4.apply_async((name,7), priority=7)
    result41.wait()
    result42.wait()
    result43.wait()
    result44.wait()
    result45.wait()
    #time.sleep(3)
    result51 = step5.apply_async((name,9), priority=9)
    result52 = step5.apply_async((name,9), priority=9)
    result53 = step5.apply_async((name,9), priority=9)
    result54 = step5.apply_async((name,9), priority=9)
    result55 = step5.apply_async((name,9), priority=9)
    result51.wait()
    result52.wait()
    result53.wait()
    result54.wait()
    result55.wait()

#
# Prerequites:
#
# 1. RabbitMQ is installed and running with default settings:
#       $ rabbitmq-server
#       # cycle RabbitMQ:
#       $ rabbitmqctl stop_app; rabbitmqctl reset; rabbitmqctl start_app
#       # list queues
#       # unacknowledged => running on a celery worker
#       # ready => ready to be handed of to a celery worker
#       $ rabbitmqctl list_queues name messages_unacknowledged messages_ready messages consumers
#
# 2. Monitor RabbitMQ:
#       => http://localhost:15672/
#
# 3. Started the celery workers (will need to restart if consumer or producer is changed):
#       $ celery worker --app=consumer:APP -c 2 --loglevel=info
#       or $ celery multi show   worker1 worker2 --app=consumer:APP -c 1 --loglevel=info
#          $ celery multi start  worker1 worker2 --app=consumer:APP -c 1 --loglevel=info
#          $ celery multi restart/stop worker1 worker2 --app=consumer:APP
#       # show workers statistics:
#       $ celery --app=consumer:APP inspect stats
#       # show configuration:
#       $ celery --app=consumer:APP inspect conf
#
# 4. Monitor celery:
#       $ flower --app=consumer:APP --port=5555 --broker_api=http://guest:guest@localhost:15672/api/
#       => http://localhost:5555/
#


import sys
if __name__ == '__main__':
    #pdb.set_trace()
    job_name = sys.argv[1] if len(sys.argv) > 1 else 'job' 

    test_task_throws_exception = True
    if test_task_throws_exception:
        try:
            # this causes an exception to be thrown by the celery worker. testing task_remote_tracebacks.
            result = do_divide_by_zero.apply_async((job_name,10),)
            result.wait()
        except:
            print(result.traceback)

    test_celery_worker_timeout = True
    if test_celery_worker_timeout:
        try:
            task_time = 30
            celery_worker_timeout = 15
            result1 = do_timelimit_test.apply_async((job_name+'-1',task_time), time_limit=celery_worker_timeout)
            result2 = do_timelimit_test.apply_async((job_name+'-2',task_time), time_limit=celery_worker_timeout)
            result3 = do_timelimit_test.apply_async((job_name+'-3',task_time), time_limit=celery_worker_timeout)
            result4 = do_timelimit_test.apply_async((job_name+'-4',task_time), time_limit=celery_worker_timeout)
            #APP.control.revoke(result1.id, terminate=True)
            result1.wait()
            result2.wait()
            result3.wait()
            result4.wait()
        except Celery3_TimeLimitExceeded as err:
            print(err)
            pass
        except Celery4_TimeLimitExceeded as err:
            # python says: celery.backends.base.TimeLimitExceeded: TimeLimitExceeded(15,)
            # closest I can find is: celery.exceptions.TimeLimitExceeded
            print(err)
            pass
        except:
            # HACK until I can figure out what exception is really being returned
            print(result1.traceback)
            pass

    test_task_caller_timeout = True
    if test_task_caller_timeout:
        try:
            task_time = 30
            task_caller_timeout = 5
            result1 = do_timelimit_test.apply_async((job_name+'-5',task_time),)
            result1.wait(timeout=task_caller_timeout)
        except TimeoutError as err:
            print(err)
            pass

    test_timeout_from_signature = True
    if test_timeout_from_signature:
        try:
            task_time = 30
            task_caller_timeout   = 15
            celery_worker_timeout = 20
            sig = signature('tasks.do_timelimit_test', args=(job_name+'-6',task_time))
            result1 = sig.apply_async(time_limit=celery_worker_timeout)
            #sig.options = { 'time_limit': celery_worker_timeout }
            #result1 = sig.delay()
            result1.wait(timeout=task_caller_timeout)
        except TimeoutError as err:
            print(err)
            pass

    test_timeout_from_group = True
    if test_timeout_from_group:
        try:
            task_time = 30
            task_caller_timeout   = 15
            celery_worker_timeout = 20
            sig = signature('tasks.do_timelimit_test', args=(job_name+'-7',task_time))
            job = group([sig,sig])
            celery_group_call = job(time_limit=celery_worker_timeout)
            result1 = celery_group_call.get(timeout=task_caller_timeout)
            print result1
        except TimeoutError as err:
            print(err)
            pass

    test_manually_chained_priority_tasks = True
    if test_manually_chained_priority_tasks:
        # bash: (python producer.py job111 &) ; sleep 3 ; (python producer.py job222 &) ; sleep 3 ; (python producer.py job333 &) ; sleep 3 ; (python producer.py job444 &) ; sleep 3 ; (python producer.py job555 &)
        # csh: python producer.py job111 & ; sleep 3 ; python producer.py job222 & ; sleep 3 ; python producer.py job333 & ; sleep 3 ; python producer.py job444 & ; sleep 3 ; python producer.py job555 &
        do_multistep_job(job_name)

    test_priority_queues = True
    if test_priority_queues:
        results = run_priority_tasks()
        num_results =len(results)
        for result in results:
            result.wait()
            # side effect of the above access is that the result message is removed from the RabbitMQ broker
            print('id(%s) status(%s) result(%i)' % (result.id, result.status, result.result))
