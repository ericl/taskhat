from task import TaskDate, Task

from time import now, make_time

def calc_offset(weekday):
   return (weekday - now().weekday()) % 7

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
   elif x.startswith('mon'):
      out = 'Monday'
      date = TaskDate(calc_offset(0))
   elif x.startswith('tue'):
      out = 'Tuesday'
      date = TaskDate(calc_offset(1))
   elif x.startswith('wed'):
      out = 'Wednesday'
      date = TaskDate(calc_offset(2))
   elif x.startswith('thu'):
      out = 'Thursday'
      date = TaskDate(calc_offset(3))
   elif x.startswith('fri'):
      out = 'Friday'
      date = TaskDate(calc_offset(4))
   elif x.startswith('sat'):
      out = 'Saturday'
      date = TaskDate(calc_offset(5))
   elif x.startswith('sun'):
      out = 'Sunday'
      date = TaskDate(calc_offset(6))
   elif x.startswith('tod') or x == 'now':
      out = 'today'
      date = TaskDate(0)
   elif x.startswith('tom'):
      out = 'tomorrow'
      date = TaskDate(1)
   elif x.startswith('yes'):
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

def end_match_f(s):
   return lambda t: t.endswith(s + ' ')

def mid_match_f(sl):
   def m(t):
      for s in sl:
         if s in t:
            return True
      return False
   return m

def stripsymb(text):
   return text.strip()[:-1]

def echo(text):
   return text

TASK_TYPES = [
   (end_match_f('!'), 'Impt task due', Task.PRIORITY_HIGH, stripsymb),
   (end_match_f('='), 'Regular task due', Task.PRIORITY_MEDIUM, stripsymb),
   (end_match_f('-'), 'Idle task due', Task.PRIORITY_LOW, stripsymb),
   (end_match_f("*"), 'Administrivia due', Task.PRIORITY_ADMIN, stripsymb),
   (mid_match_f([' hw', ' homework ']), 'Homework due', Task.PRIORITY_MEDIUM, echo),
   (mid_match_f([' proj']), 'Project due', Task.PRIORITY_HIGH, echo),
   (mid_match_f([' read ']), 'Reading due', Task.PRIORITY_LOW, echo),
   (mid_match_f([' final ', ' midterm ', ' exam ']), 'Exam on', Task.PRIORITY_HIGH, echo),
   (mid_match_f([' quiz ']), 'Quiz on', Task.PRIORITY_MEDIUM, echo),
   (mid_match_f([' turn in ', ' submit ']), 'Administrivia due', Task.PRIORITY_ADMIN, echo),
   (mid_match_f([' meet', ' go to ']), 'Appointment on', Task.PRIORITY_ADMIN, echo),
]

def derive_label(text):
   ttype = '<?> due'
   prio = Task.PRIORITY_LOW
   text = ' ' + text + ' '
   for T in TASK_TYPES:
      if T[0](text):
         ttype = T[1]
         prio = T[2]
         text = T[3](text)
         break
   out, text, date = parse_date(text)
   return (" %s %s" % (ttype, out)), text.strip(), date, prio

# vim: et sw=3
