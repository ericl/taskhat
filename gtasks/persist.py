import os
from pickle import loads, dumps

class Persist:
    def __init__(self, name):
        self.name = name
        self.path = os.environ['HOME'] + '/.gtasks-persist-' + self.name
        self.tasks = []

    def save(self, task):
        self.tasks.append(task)
        with open(self.path, 'w') as f:
            f.write(dumps(self.tasks))

    def restore(self, f_insert):
        try:
            with open(self.path, 'r') as f:
                self.tasks = loads(f.read())
                for task in self.tasks:
                    f_insert(task)
        except IOError:
            pass
