import datetime

class TaskDate:
   def __init__(self, offset_days):
      self.date = datetime.datetime.today() + datetime.timedelta(offset_days)

   def recalc_offset(self):
      return (self.date - datetime.datetime.today()).days

   def markup(self):
      # XXX make text REALLY small to match the date
      # and don't appear ugly at the same time
      return '%s/%s<span size="0"> - %s</span>' % (self.date.month, self.date.day, self.hname())

   def hname(self):
      x = self.recalc_offset()
      if x == 0:
         return 'Today'
      elif x == 1:
         return 'Tomorrow'
      elif x == 7:
         return 'Next Week'
      return self.date.strftime('%A')

   def __str__(self):
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
   # XXX make text REALLY small to match the combobox priority
   # and don't appear ugly at the same time
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
