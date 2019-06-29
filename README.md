# CeleryPriorityQueueWithRabbitMQ

First build the python 2.7 docker image which contains the celery test source code:
```bash
$ docker-compose -f docker-compose.yml build
```
This builds a single image via dockerfile, which will be shared by the `celery-boss` (Celery task producer) and the `celery-worker` (Celery task consumer/worker) docker containers within the docker-compose.

From the above command you should see:
```bash
Successfully tagged celerypriorityqueuewithrabbitmq_celery-worker:latest
Successfully tagged celerypriorityqueuewithrabbitmq_celery-boss:latest
```
If you run
```bash
$ docker images
REPOSITORY                                              TAG                 IMAGE ID            CREATED             SIZE
celerypriorityqueuewithrabbitmq_celery-worker           latest              3c20727ac4b9        14 seconds ago      940MB
celerypriorityqueuewithrabbitmq_celery-boss             latest              3c20727ac4b9        14 seconds ago      940MB
...
```
you will see that celery-boss and celery-worker share the same image.

To run the test, all you need to do is
```bash
$ time docker-compose -f docker-compose.yml up celery-boss
Starting celerypriorityqueuewithrabbitmq_rabbitmq_1 ... done
Starting celerypriorityqueuewithrabbitmq_redis_1    ... done
Recreating celerypriorityqueuewithrabbitmq_celery-worker_1 ... done
Recreating celerypriorityqueuewithrabbitmq_celery-boss_1   ... done
Attaching to celerypriorityqueuewithrabbitmq_celery-boss_1
celery-boss_1      | SUCCESS: Received divide by zero exception:
celery-boss_1      | Traceback (most recent call last):
celery-boss_1      |   File "/usr/local/lib/python2.7/site-packages/celery/app/trace.py", line 385, in trace_task
celery-boss_1      |     R = retval = fun(*args, **kwargs)
celery-boss_1      |   File "/usr/local/lib/python2.7/site-packages/celery/app/trace.py", line 648, in __protected_call__
celery-boss_1      |     return self.run(*args, **kwargs)
celery-boss_1      |   File "/app/tasks.py", line 53, in do_divide_by_zero
celery-boss_1      |     z = x / y
celery-boss_1      | ZeroDivisionError: integer division or modulo by zero
celery-boss_1      | 
celery-boss_1      | SUCCESS: TimeLimitExceeded(15,)
celery-boss_1      | SUCCESS: SoftTimeLimitExceeded()
celery-boss_1      | SUCCESS: The operation timed out.
celery-boss_1      | SUCCESS: The operation timed out.
celery-boss_1      | SUCCESS: The operation timed out.
celery-boss_1      | FINSHED: do_multistep_job.
celery-boss_1      | id(7fb5d00d-6e4a-4d7f-a948-68562e94067f) status(SUCCESS) result(1)
celery-boss_1      | id(9db16399-c315-4fdf-9921-90726605f340) status(SUCCESS) result(2)
celery-boss_1      | id(1d9b15e2-603b-4daa-b602-78127acbd1cf) status(SUCCESS) result(3)
celery-boss_1      | id(b44ae549-8b93-456a-8d41-76579629dce2) status(SUCCESS) result(4)
celery-boss_1      | id(8a6c816e-5abe-484b-819d-5a3ce98762c8) status(SUCCESS) result(5)
celery-boss_1      | id(9b74ade5-8eb7-44d2-ba14-b5c58495f2f6) status(SUCCESS) result(6)
celery-boss_1      | id(b880e051-c716-4eea-9847-26311c0170ac) status(SUCCESS) result(7)
celery-boss_1      | id(70ef6222-3fde-4ae2-a2e5-c8217fc370c7) status(SUCCESS) result(8)
celery-boss_1      | id(e8559525-7814-4afc-b0ac-7507515656a2) status(SUCCESS) result(9)
celery-boss_1      | id(45e2db19-66e5-4828-86ea-3ed15f06b340) status(SUCCESS) result(10)
celery-boss_1      | FINSHED: run_grouped_tasks.
celery-boss_1      | FINSHED: run_chord_tasks.
celery-boss_1      | Done.
celerypriorityqueuewithrabbitmq_celery-boss_1 exited with code 0

real	2m52.928s
user	0m0.735s
sys	0m0.156s
```

As a sanity check for the celerity-boss image, you can get a command prompt into the python 2.7 docker image where you can verify that the world is as it should be:
```bash
$ docker run -it --entrypoint /bin/bash <image id>
```

RabbitMQ is the Celery broker and Redis is the Celery results backend.  The code was also tested using RPC as the results backend.

The RabbitMQ management console is a part of the docker-compose and can be accessed in a browser via url `localhost:15672` (user=guest, pwd=guest).

The Redis Commander is also part of the docker-compose and can be accessed in a browser via url `localhost:8081`.  No login is required.

If you manually startup the Celery workers via
```bash
$ docker-compose -f docker-compose.yml up celery-worker
```
you should see on teardown (`docker-compose -f docker-compose.yml stop`):
```bash
celery-worker_1    | worker: Warm shutdown (MainProcess)
celery-worker_1    |  
celery-worker_1    |  -------------- celery@16c150403242 v4.3.0 (rhubarb)
celery-worker_1    | ---- **** ----- 
celery-worker_1    | --- * ***  * -- Linux-4.9.125-linuxkit-x86_64-with-debian-9.9 2019-06-28 18:53:26
celery-worker_1    | -- * - **** --- 
celery-worker_1    | - ** ---------- [config]
celery-worker_1    | - ** ---------- .> app:         tasks:0x7fd039f25250
celery-worker_1    | - ** ---------- .> transport:   amqp://guest:**@rabbitmq:5672//
celery-worker_1    | - ** ---------- .> results:     redis://redis/
celery-worker_1    | - *** --- * --- .> concurrency: 4 (prefork)
celery-worker_1    | -- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
celery-worker_1    | --- ***** ----- 
celery-worker_1    |  -------------- [queues]
celery-worker_1    |                 .> celery           exchange=celery(direct) key=celery
celery-worker_1    |                 
celery-worker_1    | 
celery-worker_1    | [tasks]
celery-worker_1    |   . tasks.do_divide_by_zero
celery-worker_1    |   . tasks.do_stuff
celery-worker_1    |   . tasks.do_timelimit_test
celery-worker_1    |   . tasks.step1
celery-worker_1    |   . tasks.step2
celery-worker_1    |   . tasks.step3
celery-worker_1    |   . tasks.step4
celery-worker_1    |   . tasks.step5
celery-worker_1    | 
celerypriorityqueuewithrabbitmq_celery-worker_1 exited with code 0
```
