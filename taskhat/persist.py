import os
from pickle import loads, dumps

from time import now

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
         s.write(dumps({'tasks': self.tasks, 'events': self.events}))
         if os.path.exists(self.path):
            os.rename(self.path, backup)
         os.rename(swap, self.path)

   def restore(self, f_insert, f_notify_events_loaded):
      try:
         with open(self.path, 'r') as f:
            saved = loads(f.read())
            self.tasks = filter(lambda t: not t.removed, saved.get('tasks', []))
            for task in self.tasks:
               f_insert(task)
            self.events = saved.get('events', [])
            f_notify_events_loaded()
      except:
         pass

# vim: et sw=3
