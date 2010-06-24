from time import now, make_timedelta

weekday_map = {0: 'M', 1: 'Tu', 2: 'W', 3: 'Th', 4: 'F', 5: 'Sa', 6: 'Su'}

def str_enum_weekdays(i):
   return weekday_map[i]

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
      for x in offsets:
         if x >= daterange[0] and x <= daterange[1]:
            return True
      return False

   def occurs_in(self, daterange):
      if self.deleted:
         return False
      return self.any_in_daterange(self.offsets_to_next(), daterange)

   def occurs_later_today(self):
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
         ret = '%s<i> - %s</i>' % (self.text, self.get_timestring())
      else:
         ret = '%s' % (self.text)
      if self.occurs_later_today():
         return ret
      else:
         return '<span strikethrough="true">%s</span>' % ret

# vim: et sw=3
