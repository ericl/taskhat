"""
Interface between human-readable file format and Taskhat's
internal structures. By default, tries to state into a
Dropbox root directory. This allows for remote viewing and
updating using Dropbox's mobile app.
"""

from taskgroup import TaskGroup
from task import Task
from time import get_today
from event import WeeklyRecurringEvent
from read_dropbox_location import read_dropbox_location
from threading import Thread
import os
import datetime
import collections

class IOWatcher(Thread):
    def __init__(self):
        super(IOWatcher, self).__init__()
        self.daemon = True
        self.monitor = True
        self.callbacks = []

    def run(self):
        while self.inotifywait():
            data = poll()
            for cb in self.callbacks:
                cb(data)

    def inotifywait(self):
        """
        Blocks until file change event happens and
        self.monitor is True
        """
        raise NotImplementedError

    def disable_change_monitoring(self):
        self.monitor = False

    def enable_change_monitoring(self):
        self.monitor = True

    def add_callback(self, cb):
        self.callbacks.append(cb)
#        cb(poll()) # TODO enable once class finished

_io_watcher = IOWatcher()
_io_watcher.start()

def get_file_loc():
    """Returns location of human-readable save file"""
    try:
        loc = read_dropbox_location()
    except:
        loc = os.path.expanduser('~/Desktop')
    return os.path.join(loc, 'Tasks')

def update(state):
    """Saves data into human-readable file format"""

    asn = collections.defaultdict(list)
    asn_keys = [g.title for g in TaskGroup.groups]

    for task in state['tasks']:
        group = TaskGroup.where_it_should_go(task)
        if not task.removed:
            asn[group.title].append(task)

    _io_watcher.disable_change_monitoring()

    with open(get_file_loc(), 'w') as out:
        print >>out, '### Tasks ###'
        print >>out
        for k in asn_keys:
            print >>out, '#', k
            for task in asn[k]:
                print >>out, task.to_human()
            print >>out

        print >>out, '### Recurring Events ###'
        print >>out
        for e in state['events']:
            if not e.deleted and e.text:
                print >>out, e.to_human()
        print >>out
        print >>out, "# Last updated:", datetime.datetime.today()

    _io_watcher.enable_change_monitoring()

def poll():
    """Returns state from current file"""

    text = open(get_file_loc(), 'r')
    tasks = []
    events = []
    parse_out = tasks
    parse_class = Task
    for line in text:
        if line.startswith('#'):
            continue
        elif line.startswith('### Recurring Events ###'):
            parse_class = WeeklyRecurringEvent
            parse_out = events
        elif line:
            parse_out.append(parse_class.from_human(line))
    return {
        'tasks': tasks,
        'events': events,
        'day': get_today(),
    }

def watch(callback):
    """Starts thread that will call back on file update"""
    _io_watcher.add_callback(callback)
