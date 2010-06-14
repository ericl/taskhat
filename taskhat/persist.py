import os
from pickle import loads, dumps

class Persist:
   def __init__(self, name):
      self.name = name
      self.path = os.environ['HOME'] + '/.taskhat-persist-' + self.name
      self.tasks = []

   def save(self, task):
      self.tasks.append(task)
      self.sync()

   def sync(self):
      with open(self.path, 'w') as f:
         f.write(dumps(self.tasks))

   def destroy(self, task):
      self.tasks.remove(task)
      self.sync()

   def restore(self, f_insert):
      try:
         with open(self.path, 'r') as f:
            self.tasks = loads(f.read())
            for task in self.tasks:
               f_insert(task)
      except IOError:
         pass

# vim: et sw=3
