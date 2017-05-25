from celery import signals

#http://docs.celeryproject.org/en/latest/userguide/signals.html#id6
#
# "Signals allows decoupled applications to receive notifications
# when certain actions occur elsewhere in the application."
#

import pdb

# Producer - executed in the process sending the task
#@signals.before_task_publish.connect
#def task_before_task_publish(sender=None, headers=None, body=None, **kwargs):
#    pdb.set_trace()
#    d = { 'sender': sender, 'headers': headers, 'body': body }
#    d.update(kwargs)
#    print('signal before_task_publish received:')
#    print(d)
#    print

# Producer - executed in the process sending the task
#@signals.after_task_publish.connect
#def task_after_task_publish(sender=None, headers=None, body=None, **kwargs):
#    d = { 'sender': sender, 'headers': headers, 'body': body }
#    d.update(kwargs)
#    print('signal after_task_publish received:')
#    print(d)
#    print

# Worker
@signals.task_prerun.connect
def task_task_prerun(sender=None, headers=None, body=None, **kwargs):
    d = { 'sender': sender, 'headers': headers, 'body': body }
    d.update(kwargs)
    print('signal task_prerun received:')
    print(d)
    print

# Worker
@signals.task_postrun.connect
def task_task_postrun(sender=None, headers=None, body=None, **kwargs):
    d = { 'sender': sender, 'headers': headers, 'body': body }
    d.update(kwargs)
    print('signal task_postrun received:')
    print(d)
    print

# Worker
@signals.task_success.connect
def task_task_success(sender=None, headers=None, body=None, **kwargs):
    d = { 'sender': sender, 'headers': headers, 'body': body }
    d.update(kwargs)
    print('signal task_success received:')
    print(d)
    print

# Worker
@signals.task_failure.connect
def task_task_failure(sender=None, headers=None, body=None, **kwargs):
    d = { 'sender': sender, 'headers': headers, 'body': body }
    d.update(kwargs)
    print('signal task_failure received:')
    print(d)
    print

# MainProcess
@signals.task_revoked.connect
def task_task_revoked(sender=None, headers=None, body=None, **kwargs):
    d = { 'sender': sender, 'headers': headers, 'body': body }
    d.update(kwargs)
    print('signal task_revoked received:')
    print(d)
    print

@signals.celeryd_after_setup.connect
def worker_celeryd_after_setup(sender=None, instance=None, **kwargs):
    d = { 'sender': sender, 'instance': instance }
    d.update(kwargs)
    print('signal celeryd_after_setup received:')
    print(d)
    print

# Exception out
#@signals.celeryd_init.connect
#def worker_celeryd_init(sender=None, instance=None, **kwargs):
#    d = { 'sender': sender, 'instance': instance }
#    d.update(kwargs)
#    print('signal celeryd_init received:')
#    print(d)
#    print

# Exception out
#@signals.worker_init.connect
#def worker_worker_init(sender=None, instance=None, **kwargs):
#    d = { 'sender': sender, 'instance': instance }
#    d.update(kwargs)
#    print('signal worker_init received:')
#    print(d)
#    print

# MainProcess
@signals.worker_ready.connect
def worker_worker_ready(sender=None, instance=None, **kwargs):
    d = { 'sender': sender, 'instance': instance }
    d.update(kwargs)
    print('signal worker_ready received:')
    print(d)
    print

# Worker
@signals.worker_process_init.connect
def worker_worker_process_init(sender=None, instance=None, **kwargs):
    d = { 'sender': sender, 'instance': instance }
    d.update(kwargs)
    print('signal worker_process_init received:')
    print(d)
    print

# Worker
@signals.worker_process_shutdown.connect
def worker_worker_process_shutdown(sender=None, instance=None, **kwargs):
    d = { 'sender': sender, 'instance': instance }
    d.update(kwargs)
    print('signal worker_process_shutdown received:')
    print(d)
    print

# MainProcess
@signals.worker_shutdown.connect
def worker_worker_shutdown(sender=None, instance=None, **kwargs):
    d = { 'sender': sender, 'instance': instance }
    d.update(kwargs)
    print('signal worker_shutdown received:')
    print(d)
    print
