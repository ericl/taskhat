import os
import file_api
from pickle import loads, dumps

from utime import now, get_today
from mira import MiraClassifier
from task import Task
from event import event_cmp

classifiers = {}
def get_classifier(key):
    global classifiers
    if not classifiers:
        load_classifiers()
    return classifiers[key]

def load_classifiers():
  path = os.environ['HOME'] + '/.taskhat-mira-prio'
  classifiers['prio'] = MiraClassifier([
      Task.PRIORITY_HIGH,
      Task.PRIORITY_MEDIUM,
      Task.PRIORITY_LOW,
      Task.PRIORITY_ADMIN,
  ], path)

class Persist:
   def __init__(self, name):
      self.name = name
      self.path = os.environ['HOME'] + '/.taskhat-persist-' + self.name
      self.pospath = os.environ['HOME'] + '/.taskhat-geom'
      self.tasks = []
      self.events = []
      self.pos = None
      self.size = None

   def save(self, task):
      self.tasks.append(task)
      self.sync()

   def resort_events(self):
      self.events.sort(event_cmp, reverse=True)

   def save_geometry(self, pos, size):
      if pos == self.pos and size == self.size:
         return
      with open(self.pospath, 'w') as f:
         self.pos = pos
         self.size = size
         f.write(dumps(pos + size))

   def restore_geometry(self, window):
      try:
         with open(self.pospath, 'r') as f:
            geom = loads(f.read())
            window.move(geom[0], geom[1])
            window.set_default_size(geom[2], geom[3])
      except IOError:
         pass

   def sync(self):
      swap = self.path + '~'
      backup = self.path + '.backup-%d' % now().weekday()
      with open(swap, 'w') as s:
         data = {
             'tasks': self.tasks,
             'events': self.events,
             'day': get_today(),
         }
         s.write(dumps(data))
         file_api.update(data)
         if os.path.exists(self.path):
            os.rename(self.path, backup)
         os.rename(swap, self.path)

   def date_to_key(self, date):
      diff = get_today() - date
      if diff.days < 0:
         return 'the future'
      elif diff.days == 0:
         return 'last restore'
      else:
         return '%d days ago' % diff.days

   def scan_past(self):
      paths = map(lambda d: '%s.backup-%d' % (self.path, d), range(0,7))
      past = []
      for path in paths:
         try:
            with open(path, 'r') as f:
               date = loads(f.read())['day']
               past.append((date, self.date_to_key(date), path))
         except IOError:
            pass
         except KeyError:
            pass
      return past

   def restore(self, f_insert, f_notify_events_loaded, path=None, f_clear=None):
      saved = self.path
      if path is not None:
         saved = path
      if f_clear:
         f_clear()
         self.tasks = []
         self.events = []
      try:
         with open(saved, 'r') as f:
            saved = loads(f.read())
            self.tasks = filter(lambda t: not t.removed, saved.get('tasks', []))
            for task in self.tasks:
               f_insert(task)
            self.events = filter(lambda e: not e.deleted, saved.get('events', []))
      except Exception, e:
         print e
      f_notify_events_loaded()

# vim: et sw=3
