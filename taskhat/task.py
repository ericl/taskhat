from time import make_timedelta, get_today

class TaskDate:
   FUTURE = 999999
   SOON = 999998
   def __init__(self, offset_days=None, date=None):
      if date:
         self.date = date
      elif offset_days is None:
         self.date = None
      elif offset_days is TaskDate.FUTURE:
         self.date = TaskDate.FUTURE
      elif offset_days is TaskDate.SOON:
         self.date = TaskDate.SOON
      else:
         self.date = get_today() + make_timedelta(offset_days)
   
   def special(self):
      return self.date is None or self.date == TaskDate.FUTURE or self.date == TaskDate.SOON

   def offset(self):
      if self.date is None:
         return -TaskDate.FUTURE
      elif self.date == TaskDate.FUTURE:
         return TaskDate.FUTURE
      elif self.date == TaskDate.SOON:
         return 3
      return (self.date - get_today()).days

   def markup(self):
      """Returns same text as __str__, but with markup to hide extraneous text.
         This enables the combobox to match the strings."""
      if self.date is None:
         # emulate a horizontal dash
         return '<span strikethrough="true" size="700">No Date</span>'
      elif self.date == TaskDate.FUTURE:
         return '<span size="1">In the </span>Future'
      elif self.date == TaskDate.SOON:
         return '<span size="1">Sometime </span>Soon'
      x = self.hname()
      if x == 'In 1 Week':
         return '%s/%s - <span size="1">In </span>1 W<span size="1">ee</span>k' % (self.date.month, self.date.day)
      elif x == 'Today':
         return '%s/%s - Today' % (self.date.month, self.date.day)
      elif x == 'Tomorrow':
         return '%s/%s - Tomorrow' % (self.date.month, self.date.day)
      return '%s/%s - %s<span size="0">%s</span>' % (self.date.month, self.date.day, x[:3], x[3:])

   def hname(self):
      x = self.offset()
      if x == 0:
         return 'Today'
      elif x == 1:
         return 'Tomorrow'
      elif x == 7:
         return 'In 1 Week'
      return self.date.strftime('%A')

   def __str__(self):
      if self.date is None:
         return 'No Date'
      elif self.date == TaskDate.FUTURE:
         return 'In the Future'
      elif self.date == TaskDate.SOON:
         return 'Sometime Soon'
      return '%s/%s - %s' % (self.date.month, self.date.day, self.hname())

class Priority:
   def __init__(self, num, name):
      self.num = num
      self.name = name

   def __str__(self):
      return self.name

   def __equal__(self, other):
      return self.num == other.num

class Task:
   PRIORITY_ADMIN = Priority(0, '\xe2\x87\xa1')
   PRIORITY_HIGH = Priority(1, '\xe2\x87\x91')
   PRIORITY_MEDIUM = Priority(2, '\xe2\x86\x91')
   PRIORITY_LOW = Priority(3, '-')

   def __init__(self, text, date, prio):
      self.text = text
      self.date = date
      self.prio = prio
      self.removed = False
      self.prefix = ''

   def to_human(self):
      return '%s | %s | %s' % (self.prio, self.text, self.date)

   @staticmethod
   def from_human(text):
      raise NotImplementedError

   def prio_match(self, text):
      if text == Task.PRIORITY_LOW.name:
         return Task.PRIORITY_LOW
      if text == Task.PRIORITY_MEDIUM.name:
         return Task.PRIORITY_MEDIUM
      if text == Task.PRIORITY_HIGH.name:
         return Task.PRIORITY_HIGH
      if text == Task.PRIORITY_ADMIN.name:
         return Task.PRIORITY_ADMIN
      assert False

   def match_date(self, value):
      for i in range(0, 8):
         x = TaskDate(i)
         if value == str(x):
            return x
      n = TaskDate(None)
      if value == str(n):
         return n
      n = TaskDate(TaskDate.FUTURE)
      if value == str(n):
         return n
      n = TaskDate(TaskDate.SOON)
      if value == str(n):
         return n
      return None

   def __str__(self):
      return self.text

# vim: et sw=3
