from task import TaskDate, Task

from datetime import datetime

def calc_offset(weekday):
   return weekday - datetime.today().weekday()

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
      today = datetime.today()
      try:
         x = x.split('/')
         a = datetime(today.year, int(x[0]), int(x[1]))
         b = datetime(today.year + 1, int(x[0]), int(x[1]))
         if (a - today).days < -30:
            out = "%s next year" % b.strftime("%B %d")
            date = TaskDate(date=b)
         elif (a - today).days < 0:
            out = "%s (past)" % a.strftime("%B %d")
            date = TaskDate(date=a)
         else:
            out = a.strftime("%B %d")
            date = TaskDate(date=a)
      except:
         found = False
   elif x.startswith('mon'):
      out = 'Monday'
      date = TaskDate(0)
   elif x.startswith('tue'):
      out = 'Tuesday'
      date = TaskDate(1)
   elif x.startswith('wed'):
      out = 'Wednesday'
      date = TaskDate(2)
   elif x.startswith('thu'):
      out = 'Thursday'
      date = TaskDate(3)
   elif x.startswith('fri'):
      out = 'Friday'
      date = TaskDate(4)
   elif x.startswith('sat'):
      out = 'Saturday'
      date = TaskDate(5)
   elif x.startswith('sun'):
      out = 'Sunday'
      date = TaskDate(6)
   elif x.startswith('tod') or x == 'now':
      out = 'today'
      date = TaskDate(0)
   elif x.startswith('tom'):
      out = 'tomorrow'
      date = TaskDate(1)
   elif x.startswith('yest'):
      out = 'yesterday'
      date = TaskDate(-1)
   elif x.startswith('nex'):
      out = 'next week'
      date = TaskDate(7)
   elif x.startswith('fut') or x.startswith('lat'):
      out = 'in the future'
      date = TaskDate(TaskDate.FUTURE)
   else:
      found = False
   if found:
      text = ' '.join(text.split()[:-1])
   return out, text, date

def derive_label(text):
   ttype = '<?>'
   parse = False
   verb = 'due'
   prio = Task.PRIORITY_LOW
   if text.endswith('!'):
      ttype = 'Important task'
      prio = Task.PRIORITY_HIGH
   elif text.endswith('='):
      ttype = 'Regular task'
      prio = Task.PRIORITY_MEDIUM
   elif text.endswith('-'):
      ttype = 'Idle task'
      prio = Task.PRIORITY_LOW
   elif text.endswith('*'):
      ttype = 'Administrivia'
      prio = Task.PRIORITY_ADMIN
   else:
      parse = True
   if parse:
      text = ' ' + text + ' '
      if ' hw ' in text or ' homework ' in text:
         ttype = 'Homework'
         prio = Task.PRIORITY_MEDIUM
      if ' proj' in text:
         ttype = 'Project'
         prio = Task.PRIORITY_HIGH
      if ' read ' in text:
         ttype = 'Reading'
         prio = Task.PRIORITY_LOW
      if ' final ' in text or ' midterm ' in text or ' exam ' in text:
         ttype = 'Exam'
         verb = 'on'
         prio = Task.PRIORITY_HIGH
      if ' quiz ' in text:
         ttype = 'Quiz'
         verb = 'on'
         prio = Task.PRIORITY_MEDIUM
      if ' turn in ' in text:
         ttype = 'Administrivia'
         prio = Task.PRIORITY_ADMIN
   else:
      text = text[:-1]
   out, text, date = parse_date(text)
   return (" %s %s %s" % (ttype, verb, out)), text.strip(), date, prio

# vim: et sw=3
