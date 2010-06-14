import datetime

class TaskDate:
   def __init__(self, offset_days):
      if offset_days is None:
         self.date = None
      else:
         self.date = self.get_today() + datetime.timedelta(offset_days)

   def get_today(self):
      now = datetime.datetime.today()
      today = datetime.datetime(now.year, now.month, now.day)
      return today

   def recalc_offset(self):
      return (self.date - self.get_today()).days

   def markup(self):
      """Returns same text as __str__, but with markup to hide extraneous text.
         This enables the combobox to match the strings."""
      if self.date is None:
         return '<span size="0">No Date</span>'
      return '%s/%s<span size="0"> - %s</span>' % (self.date.month, self.date.day, self.hname())

   def hname(self):
      if self.date is None:
         return 'None'
      x = self.recalc_offset()
      if x == 0:
         return 'Today'
      elif x == 1:
         return 'Tomorrow'
      elif x == 7:
         return 'Next Week'
      return self.date.strftime('%A')

   def __str__(self):
      if self.date is None:
         return 'No Date'
      return '%s/%s - %s' % (self.date.month, self.date.day, self.hname())

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
   PRIORITY_ADMIN = Priority(0, 'Administrivia (*)', '<span size="1">Administrivia (</span>*<span size="0">)</span>')
   PRIORITY_HIGH = Priority(1, 'High (!)', '<span size="1">High (</span>!<span size="0">)</span>')
   PRIORITY_MEDIUM = Priority(2, 'Medium (=)', '<span size="1">Medium (</span>=<span size="0">)</span>')
   PRIORITY_LOW = Priority(3, 'Low (-)', '<span size="1">Low (</span>-<span size="0">)</span>')

   def __init__(self, text, date, prio):
      self.text = text
      self.date = date
      self.prio = prio
      self.removed = False

# vim: et sw=3
