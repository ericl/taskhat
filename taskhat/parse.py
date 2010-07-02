from task import TaskDate, Task

from time import now, make_time

from config import DATE_MATCH_DICT, TYPE_MATCHES

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
   if '/' in x:
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
      out, date, found = DATE_MATCH_DICT.get(x[0:3], [out, date, False])
   else:
      found = False
   if found:
      text = ' '.join(text.split()[:-1])
   return out, text, date

def label_from_string(text):
   text = text.strip()
   ttype = '<?> due'
   prio = Task.PRIORITY_LOW
   text = ' ' + text + ' '
   for T in TYPE_MATCHES:
      if T[0](text):
         ttype = T[1]
         prio = T[2]
         text = T[3](text)
         break
   out, text, date = parse_date(text)
   return (" %s %s" % (ttype, out)), text.strip(), date, prio

def task_from_string(text):
   res = label_from_string(text)
   text = res[1]
   if not text:
      text = '<?>'
   return Task(text, res[2], res[3])

# vim: et sw=3
