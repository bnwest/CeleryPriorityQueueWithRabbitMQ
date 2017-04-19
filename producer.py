import time
from consumer import APP

@APP.task(queue='celery') # add priority= here
def do_stuff(priority):
    time.sleep(5)
    return priority

def run_tasks():
    results = [ do_stuff.apply_async((pri,),  priority=pri) for pri in range (1,11) ]

    # no priority appears to have a lower priority than the lowest priority, for the win.
    # zero priority is an undocumented thing, which appears to be equivalent to no priority
    results.append( do_stuff.apply_async((0,)            ) )
    results.append( do_stuff.apply_async((1,), priority=1) )
    results.append( do_stuff.apply_async((1,), priority=1) )
    results.append( do_stuff.apply_async((99,), priority=0) )
    results.append( do_stuff.apply_async((0,)            ) )

    return results

# Prerequites:
#
# 1. RabbitMQ is installed and running with default settings:
#       $ rabbitmq-server
#
# 2. Started the celery workers:
#       $ celery worker --app=consumer:APP -c 2 --loglevel=info

if __name__ == '__main__':
    results = run_tasks()
    num_results =len(results)
    for result in results:
        result.wait()
        print('id(%s) status(%s) result(%i)' % (result.id, result.status, result.result))
