class Priority:
   def __init__(self, num, name, symb):
      self.num = num
      self.name = name
      self.symb = symb

   def symbol(self):
      return self.symb

   def __str__(self):
      return self.name

class Task:
   PRIORITY_ADMIN = Priority(0, 'Administrivia', '  *  ')
   PRIORITY_HIGH = Priority(1, 'High', '  !  ')
   PRIORITY_MEDIUM = Priority(2, 'Medium', '  =  ')
   PRIORITY_LOW = Priority(3, 'Low', '  -  ')

   def __init__(self, text, date, prio):
      self.text = text
      self.date = date
      self.prio = prio
      self.removed = False

   def pretty_date(self):
      return '6/13'

# vim: et sw=3
