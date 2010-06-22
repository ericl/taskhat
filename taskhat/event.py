from datetime import datetime

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
      today = datetime.today().weekday()
      return map(lambda d: (d - today) % 7, self.days)

   def any_in_daterange(self, offsets, daterange):
      for x in offsets:
         if x >= daterange[0] and x <= daterange[1]:
            return True
      return False

   def occurs_in(self, daterange):
      return self.any_in_daterange(self.offsets_to_next(), daterange)

# vim: et sw=3
