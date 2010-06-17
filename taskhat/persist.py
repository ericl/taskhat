import os
from pickle import loads, dumps

class Persist:
   def __init__(self, name):
      self.name = name
      self.path = os.environ['HOME'] + '/.taskhat-persist-' + self.name
      self.pospath = os.environ['HOME'] + '/.taskhat-geom'
      self.tasks = []
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
      with open(self.path, 'w') as f:
         f.write(dumps(self.tasks))

   def restore(self, f_insert):
      try:
         with open(self.path, 'r') as f:
            self.tasks = filter(lambda t: not t.removed, loads(f.read()))
            for task in self.tasks:
               f_insert(task)
      except IOError:
         pass

# vim: et sw=3
