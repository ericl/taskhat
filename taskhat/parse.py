import re

from task import TaskDate, Task
from utime import now, make_time
from config import DATE_MATCH_DICT
from ngrams import ngen
import persist

def parse_date(text):
   x = None
   out = '<?>'
   date = TaskDate(None)
   try:
      x = text.split()[-1]
   except:
      return '<?>', text, date
   x = x.lower()
   found = True
   if re.match(r'\d{1,2}/\d{1,2}/\d{4}', x):
      out = x
      x = map(int, x.split('/'))
      date = TaskDate(date=make_time(x[2], x[0], x[1]))
   elif '/' in x:
      today = now()
      try:
         x = x.split('/')
         a = make_time(today.year, int(x[0]), int(x[1]))
         b = make_time(today.year + 1, int(x[0]), int(x[1]))
         if (a - today).days < -30:
            out = "%s next year" % b.strftime("%b %d")
            date = TaskDate(date=b)
         elif (a - today).days < 0:
            out = "%s (past)" % a.strftime("%b %d")
            date = TaskDate(date=a)
         else:
            out = a.strftime("%b %d")
            date = TaskDate(date=a)
      except:
         found = False
   elif len(x) >= 3:
      o, f = out, found # save in case date match fails
      verify, out, f_date, found = DATE_MATCH_DICT.get(x[0:3], ['', out, lambda: date, False])
      if found and not verify.startswith(x):
         out, found = o, f # reset on failed date match
      else:
         date = f_date() # assign date
   else:
      found = False
   if found:
      text = ' '.join(text.split()[:-1])
   return out, text, date

def label_from_string(text):
   text = text.strip()
   prio = persist.get_classifier('prio').classify(ngen(text))
   text = ' ' + text + ' '
   out, text, date = parse_date(text)
   ttype = {
       Task.PRIORITY_HIGH: 'Important task due',
       Task.PRIORITY_MEDIUM: 'Assignment due',
       Task.PRIORITY_LOW: 'Task for',
       Task.PRIORITY_ADMIN: 'Appointment on',
   }[prio]
   return (" %s %s" % (ttype, out)), text.strip(), date, prio

def task_from_string(text):
   res = label_from_string(text)
   text = res[1]
   if not text:
      text = '<?>'
   return Task(text, res[2], res[3])

# vim: et sw=3
