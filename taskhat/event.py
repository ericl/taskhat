from time import now

def str_enum_weekdays(i):
   return {0: 'M', 1: 'Tu', 2: 'W', 3: 'Th', 4: 'F', 5: 'Sa', 6: 'Su'}[i]

class Event(object):
   def __init__(self, text):
      self.text = text
   
   def occurs_in(self, daterange):
      return True

class WeeklyRecurringEvent(Event):
   def __init__(self, text, days):
      super(WeeklyRecurringEvent, self).__init__(text)
      self.days = days

   def offsets_to_next(self):
      today = now().weekday()
      return map(lambda d: (d - today) % 7, self.days)

   def any_in_daterange(self, offsets, daterange):
      for x in offsets:
         if x >= daterange[0] and x <= daterange[1]:
            return True
      return False

   def occurs_in(self, daterange):
      return self.any_in_daterange(self.offsets_to_next(), daterange)

   def __str__(self):
      return "[%s] %s" % (''.join(map(str_enum_weekdays, self.days)), self.text)

# vim: et sw=3
