from time import now, make_timedelta
import re

from taskgroup import escape

weekday_map = {0: 'M', 1: 'Tu', 2: 'W', 3: 'Th', 4: 'F', 5: 'Sa', 6: 'Su'}

def str_enum_weekdays(i):
   return weekday_map[i]

def event_cmp(e1, e2):
   if not e2.tdelta and e1.tdelta:
      return 1
   if not e1.tdelta and e2.tdelta:
      return -1
   if e2.tdelta == e1.tdelta:
      return 0
   elif e2.tdelta > e1.tdelta:
      return 1
   else:
      return -1

def event_sort_func(model, iter1, iter2):
   e1 = model.get_value(iter1, 0)
   e2 = model.get_value(iter2, 0)
   return event_cmp(e1, e2)

class Event(object):
   def __init__(self, text):
      self.text = text
      self.deleted = False
   
   def occurs_in(self, daterange):
      return not self.deleted

   def occurs_later_today(self):
      return not self.deleted

class WeeklyRecurringEvent(Event):
   def __init__(self, text, days, tdelta):
      super(WeeklyRecurringEvent, self).__init__(text)
      self.days = days
      self.tdelta = tdelta

   def to_human(self):
      return '%s | %s | %s' % (self.text, self.days, self.tdelta)

   @staticmethod
   def from_human(text):
      try:
         text, days, tdelta = text.split('|')
         text = text.strip()
         days = sorted(set(map(int, re.findall('[0-6]', days))))
         tdelta = WeeklyRecurringEvent.parse_timestring(tdelta)
      except:
         days = range(7)
         tdelta = WeeklyRecurringEvent.parse_timestring('')
      return WeeklyRecurringEvent(text, days, tdelta)

   @classmethod
   def parse_datestring(cls, datestring):
      days = []
      for k in weekday_map:
         if weekday_map[k] in datestring:
            days.append(k)
      return days

   @classmethod
   def parse_timestring(cls, timestring):
      hours = 0
      minutes = 0
      timestring = filter(lambda c: c.isdigit() or c in ':apm', timestring)
      if timestring.endswith('pm') or timestring.endswith('am'):
         if timestring.endswith('pm'):
            hours += 12
         timestring = timestring[:-2]
      m = timestring.split(':')
      if len(m) > 0:
         try:
            x = int(m[0])
            if x == 12 and hours == 12:
               pass
            else:
               hours += x
         except:
            pass
      if len(m) > 1:
         try:
            minutes = int(m[1])
         except:
            pass
      return make_timedelta(hours=hours, minutes=minutes)

   @classmethod
   def from_text(cls, text, datestring, timestring):
      days = WeeklyRecurringEvent.parse_datestring(datestring)
      tdelta = WeeklyRecurringEvent.parse_timestring(timestring)
      return cls(text, days, tdelta)

   def offsets_to_next(self):
      today = now().weekday()
      return map(lambda d: (d - today) % 7, self.days)

   def any_in_daterange(self, offsets, daterange):
      def isnt_offset(val):
         return val > 7 or val is None
      for x in offsets:
         if (isnt_offset(daterange[0]) or x >= daterange[0]) \
            and (isnt_offset(daterange[1]) or x <= daterange[1]):
            return True
      return False

   def occurs_in(self, daterange):
      if self.deleted:
         return False
      return self.any_in_daterange(self.offsets_to_next(), daterange)

   def occurs_later_today(self):
      if self.deleted:
         return False
      if self.tdelta.seconds == 0:
         return True
      x = now()
      return self.tdelta.seconds > 3600*x.hour + 60*x.minute

   def get_datestring(self):
      return''.join(map(str_enum_weekdays, self.days))

   def get_timestring(self):
      if not self.tdelta.seconds:
         return ''
      suffix = 'am'
      hours = self.tdelta.seconds / 3600
      minutes = (self.tdelta.seconds % 3600) / 60
      if hours == 12:
         suffix = 'pm'
      elif hours > 12:
         hours -= 12
         suffix = 'pm'
      return '%d:%02d%s' % (hours, minutes, suffix)

   def __str__(self):
      if self.tdelta.seconds:
         return '%s<i> - %s</i>' % (escape(self.text), self.get_timestring())
      return '%s' % (self.text)

   def __repr__(self):
      return 'WeeklyRecurringEvent(%s, %s, %s)' % (self.text, self.days, self.tdelta)

# vim: et sw=3
