import os
from pickle import loads, dumps

class Persist:
   def __init__(self, name):
      self.name = name
      self.path = os.environ['HOME'] + '/.taskhat-persist-' + self.name
      self.pospath = os.environ['HOME'] + '/.taskhat-geom'
      self.tasks = []

   def save(self, task):
      self.tasks.append(task)
      self.sync()

   def save_geometry(self, pos, size):
      with open(self.pospath, 'w') as f:
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
            self.tasks = loads(f.read())
            for task in self.tasks:
               if not task.removed:
                  f_insert(task)
      except IOError:
         pass

# vim: et sw=3
