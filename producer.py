import time
import pdb


from celery.exceptions    import TimeoutError
from billiard.exceptions  import TimeLimitExceeded as Celery3_TimeLimitExceeded
from celery.exceptions    import TimeLimitExceeded as Celery4_TimeLimitExceeded
from celery.exceptions    import SoftTimeLimitExceeded

from consumer import APP
from tasks import *

from celery import signature, group, chain, chord

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

def run_chained_tasks():
    sigs = [  signature('tasks.do_stuff', args=(pri,), immutable=True,  priority=pri) for pri in range (1,11) ]
    chained_tasks = chain(sigs)
    res = chained_tasks()
    res.get()
    return res

def run_grouped_tasks():
    sigs = [  signature('tasks.do_stuff', args=(pri,), immutable=True,  priority=pri) for pri in range (1,11) ]
    grouped_tasks = group(sigs)
    res = grouped_tasks()
    res.get()
    return res.results

def run_chord_tasks():
    sigs = [  signature('tasks.do_stuff', args=(pri,), immutable=True,  priority=pri) for pri in range (1,5) ]
    header = sigs[0:3]
    callback = sigs[3]
    grouped_tasks = group(sigs[0:3])

    # NotImplementedError (not all results backend support chord):
    # res = chord(header)(callback)

    # NotImplementedError (below chain gets converted implicitly to  a chord and thus has same issue as above):
    # res = chain(grouped_tasks, callback)()

    # do it manually:
    res = grouped_tasks()
    res.get()
    results = res.results
    res =  callback.delay()
    res.get()
    results.append(res)

    return results

def run_sig_chain_group_tasks():
    sigs = [  signature('tasks.do_stuff', args=(pri,), immutable=True,  priority=pri) for pri in range (1,11) ]
    sig = sigs[0]
    chained_tasks = chain(sigs[1:4])
    grouped_tasks = group(sigs[4:7])

    # chain( sig, chain, group )
    mother_of_all_tasks = chain(sig, chained_tasks, grouped_tasks)
    res = mother_of_all_tasks()
    res.get()

    # chain( sig, group, chain ) # NotImplementedError
    # chain( chain, group, sig ) # NotImplementedError
    # chain( chain, sig, group ) # infinite stroll
    # chain( group, sig, chain ) # NotImplementedError
    # chain( group, chain, sig ) # NotImplementedError
    # group( sig, group, chain ) # infinite stroll
    # group( sig, chain, group ) # infinite stroll
    # group( chain, sig, group ) # infinite stroll
    # group( chain, group, sig ) # infinite stroll
    # group( group, sig, chain ) # infinite stroll
    # group( group, chain, sig ) # infinite stroll

    return res

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
            print("Failed to receive a ZeroDivisionError exception.")
        except ZeroDivisionError as err:
            print("SUCCESS: Received divide by zero exception:")
            print(result.traceback)

    test_celery_worker_hard_timeout = True
    if test_celery_worker_hard_timeout:
        try:
            task_time = 30
            celery_worker_hard_timeout = 15
            result1 = do_timelimit_test.apply_async((job_name+'-1',task_time), time_limit=celery_worker_hard_timeout)
            result2 = do_timelimit_test.apply_async((job_name+'-2',task_time), time_limit=celery_worker_hard_timeout)
            result3 = do_timelimit_test.apply_async((job_name+'-3',task_time), time_limit=celery_worker_hard_timeout)
            result1.wait()
            result2.wait()
            result3.wait()
            print("FAIL: expecting a worker hard timeout before task completion.")
            # expecting the celery worker task to timeout before completion,
            # which will cause the main celery process to kill and restart its child and
            # which will cause one of the above wait() calls to throw an exception
        except Celery3_TimeLimitExceeded as err:
            print("SUCCESS: " + str(err))
        except Celery4_TimeLimitExceeded as err:
            # python says: celery.backends.base.TimeLimitExceeded: TimeLimitExceeded(15,)
            # closest I can find is: celery.exceptions.TimeLimitExceeded
            print("SUCCESS: " + str(err))
        except:
            # HACK until I can figure out what exception is really being returned
            print("SUCCESS: Hanndling a TimeLimitExceeded like from the celery worker:")
            print(result1.traceback)

    test_celery_worker_soft_timeout = True
    if test_celery_worker_soft_timeout:
        try:
            task_time = 30
            celery_worker_soft_timeout = 15
            celery_worker_hard_timeout = 20
            result1 = do_timelimit_test.apply_async((job_name+'-4',task_time),
                                                    time_limit=celery_worker_hard_timeout,
                                                    soft_time_limit=celery_worker_soft_timeout)
            result1.wait()
            print("FAIL: expecting a worker soft timeout before task completion.")
            # expecting the celery worker task to timeout before completion,
            # which cause the celery worker (childof the main) to experience an unhandled soft time out exception and
            # which propagate to the wait() call 
        except SoftTimeLimitExceeded as err:
            print("SUCCESS: " + str(err))
        except:
            # HACK until I can figure out what exception is really being returned
            print("SUCCESS: Hanndling a SoftTimeLimitExceeded like from the celery worker:")
            print(result1.traceback)

    test_task_caller_timeout = True
    if test_task_caller_timeout:
        try:
            task_time = 30
            task_caller_timeout = 5
            result1 = do_timelimit_test.apply_async((job_name+'-5',task_time),)
            result1.wait(timeout=task_caller_timeout)
            print("FAIL: expecting a call site timeout before task completion.")
            # expecting the wait() call to timeout and throw a TimeoutError exception and
            # the celery worker task will complete successfully
        except TimeoutError as err:
            #APP.control.revoke(result1.id, terminate=True)
            print("SUCCESS: " + str(err))

    test_timeout_from_signature = True
    if test_timeout_from_signature:
        try:
            task_time = 30
            task_caller_timeout = 15
            celery_worker_soft_timeout = 20
            celery_worker_hard_timeout = 25
            sig = signature('tasks.do_timelimit_test', args=(job_name+'-6',task_time))
            result1 = sig.apply_async(time_limit=celery_worker_hard_timeout,soft_time_limit=celery_worker_soft_timeout)
            #sig.options = { 'time_limit': celery_worker_timeout }
            #result1 = sig.delay()
            result1.wait(timeout=task_caller_timeout)
            print("FAIL: expecting a worker soft timeout before task completion.")
            # expecting the wait() call to timeout and throw a TimeoutError exception and
            # the celery worker task will complete successfully
        except TimeoutError as err:
            print("SUCCESS: " + str(err))

    test_timeout_from_group = True
    if test_timeout_from_group:
        try:
            task_time = 30
            task_caller_timeout   = 15
            celery_worker_soft_timeout = 20
            celery_worker_hard_timeout = 25
            sig = signature('tasks.do_timelimit_test', args=(job_name+'-7',task_time))
            job = group([sig,sig])
            celery_group_call = job(time_limit=celery_worker_hard_timeout,soft_time_limit=celery_worker_soft_timeout)
            result1 = celery_group_call.get(timeout=task_caller_timeout)
            print("FAIL: expecting a call site or worker timeout before group task completion.")
            # expecting the get() call to timeout and throw a TimeoutError exception and
            # the celery worker task will complete successfully
        except TimeoutError as err:
            print("SUCCESS: " + str(err))

    test_manually_chained_priority_tasks = True
    if test_manually_chained_priority_tasks:
        # bash: (python producer.py job111 &) ; sleep 3 ; (python producer.py job222 &) ; sleep 3 ; (python producer.py job333 &) ; sleep 3 ; (python producer.py job444 &) ; sleep 3 ; (python producer.py job555 &)
        # csh: python producer.py job111 & ; sleep 3 ; python producer.py job222 & ; sleep 3 ; python producer.py job333 & ; sleep 3 ; python producer.py job444 & ; sleep 3 ; python producer.py job555 &
        do_multistep_job(job_name)
        print('FINSHED: do_multistep_job.')

    test_priority_queues = True
    if test_priority_queues:
        results = run_priority_tasks()
        num_results =len(results)
        for result in results:
            result.wait()
            # side effect of the above access is that the result message is removed from the RabbitMQ broker
            # flower will show the actual, priority execution order of the tasks
            print('id(%s) status(%s) result(%i)' % (result.id, result.status, result.result))

    test_chain_tasks = False
    if test_chain_tasks:
        run_chained_tasks()
        print('FINSHED: run_chained_tasks.')

    test_group_tasks = True
    if test_group_tasks:
        # since tasks are submitted as a group, you should see priority queue behavior in flower
        run_grouped_tasks()
        print('FINSHED: run_grouped_tasks.')

    test_chord_tasks = True
    if test_chord_tasks:
        # lesson learned: do not use chords.
        run_chord_tasks()
        print('FINSHED: run_chord_tasks.')

    test_canvas_aggregation = False
    if test_canvas_aggregation:
        # lesson learned: do not do this. only chain or group signatures.  need more? do it manually.
        res = run_sig_chain_group_tasks()
        print('FINSHED: run_sig_chain_group_tasks.')

    print('Done.')
    # sys.exit(0xDEADBEEF)
