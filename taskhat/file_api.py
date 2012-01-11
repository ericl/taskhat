"""
Interface between human-readable file format and Taskhat's
internal structures. By default, tries to state into a
Dropbox root directory. This allows for remote viewing and
updating using Dropbox's mobile app.
"""

from taskgroup import TaskGroup
from task import Task
from time import get_today, now
from event import WeeklyRecurringEvent
from read_dropbox_location import read_dropbox_location
from threading import Thread
import os
import sys
import inotifyx
import datetime
import collections
import gobject

gobject.threads_init()

# establish file store directory
try:
    FILE_DIR = read_dropbox_location()
except:
    FILE_DIR = os.path.expanduser('~/Desktop')
FILE_NAME = 'Tasks.txt'
FILE_PATH = os.path.join(FILE_DIR, FILE_NAME)

class IOWatcher(Thread):
    def __init__(self):
        super(IOWatcher, self).__init__()
        self.daemon = True
        self.last_update = datetime.datetime(1970,1,1)
        self.callbacks = []
        self.fd = inotifyx.init()
        self.wd = inotifyx.add_watch(self.fd, FILE_DIR)
        self.NOTABLE = inotifyx.IN_CLOSE_WRITE | inotifyx.IN_MOVE

    def run(self):
        while self.inotifywait():
            try:
                data = poll()
                for cb in self.callbacks:
                    cb(data)
            except Exception, e:
                print "Ignored bad read", e

    def inotifywait(self):
        """
        Blocks until file change event happens and
        self.last_update is not recent
        """
        while True:
            events = inotifyx.get_events(self.fd)
            if (now() - self.last_update).total_seconds() < 1.0:
                continue
            for e in events:
                sys.stdout.flush()
                if e.name == FILE_NAME and e.mask & self.NOTABLE:
                    while inotifyx.get_events(self.fd, 0.5):
                        pass
                    return True

    def pause_change_monitoring(self):
        self.last_update = now()

    def add_callback(self, cb):
        self.callbacks.append(cb)
        data = poll()
        try:
            cb(data)
        except Exception, e:
            print "Error adding", cb, e

_io_watcher = IOWatcher()
_io_watcher.start()

def update(state):
    """Saves data into human-readable file format"""

    print "Writing state to file"

    asn = collections.defaultdict(list)
    asn_keys = [g.title for g in TaskGroup.groups]

    for task in state['tasks']:
        group = TaskGroup.where_it_should_go(task)
        if not task.removed:
            asn[group.title].append(task)

    _io_watcher.pause_change_monitoring()

    with open(FILE_PATH, 'w') as out:
        print >>out, '### Tasks ###'
        print >>out, '# TYPE NEW TASKS HERE:'
        print >>out
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

def poll():
    """
    Returns state from current file.
    Raises if file is malformed.
    """

    print "Reading state from file"
    text = open(FILE_PATH, 'r').read().split('\n')
    tasks = []
    events = []
    parse_out = tasks
    parse_class = Task
    if text[0] != '### Tasks ###':
        raise Exception
    for line in text:
        if line.startswith('### Recurring Events ###'):
            parse_class = WeeklyRecurringEvent
            parse_out = events
        elif line.startswith('#'):
            continue
        elif line:
            parse_out.append(parse_class.from_human(line))
    if not tasks:
        raise Exception
    return {
        'tasks': tasks,
        'events': events,
        'day': get_today(),
    }

def watch(callback):
    """Starts thread that will call back on file update"""
    _io_watcher.add_callback(callback)
