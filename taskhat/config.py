from task import Task, TaskDate

from time import days_until_this_weekday

# run_in_background: don't quit with window close
#   - enables fast startup
#   - may not play nice with wm focus prevention
CONFIG = {'run_in_background': True}

# starts_with_text: [status text, date, strip_date_from_end]
DATE_MATCH_DICT = {
   'mon': ['Monday', TaskDate(days_until_this_weekday(0)), True],
   'tue': ['Tuesday', TaskDate(days_until_this_weekday(1)), True],
   'wed': ['Wednesday', TaskDate(days_until_this_weekday(2)), True],
   'thu': ['Thursday', TaskDate(days_until_this_weekday(3)), True],
   'fri': ['Friday', TaskDate(days_until_this_weekday(4)), True],
   'sat': ['Saturday', TaskDate(days_until_this_weekday(5)), True],
   'sun': ['Sunday', TaskDate(days_until_this_weekday(6)), True],
   'tod': ['today', TaskDate(0), True],
   'now': ['today', TaskDate(0), True],
   'tom': ['tomorrow', TaskDate(1), True],
   'yes': ['tomorrow', TaskDate(-1), True],
   'nex': ['next week', TaskDate(7), True],
   'soo': ['soon', TaskDate(TaskDate.SOON), True],
   'fut': ['in the future', TaskDate(TaskDate.FUTURE), True],
   'lat': ['in the future', TaskDate(TaskDate.FUTURE), True],
}

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

# (matcher function, status text, assigned priority, post-processing function)
TYPE_MATCHES = [
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
