from task import Task, TaskDate

from time import days_until_this_weekday

# run_in_background: don't quit with window close
#   - enables fast startup
#   - may not play nice with wm focus prevention
# show_recurring_events: show daily schedule and such in main window
CONFIG = {'run_in_background': True,
          'show_recurring_events': False}

# starts_with_text: [status text, f_date, strip_date_from_end]
DATE_MATCH_DICT = {
   'mon': ['monday', 'Monday', lambda: TaskDate(days_until_this_weekday(0)), True],
   'tue': ['tuesday', 'Tuesday', lambda: TaskDate(days_until_this_weekday(1)), True],
   'wed': ['wednesday', 'Wednesday', lambda: TaskDate(days_until_this_weekday(2)), True],
   'thu': ['thursday', 'Thursday', lambda: TaskDate(days_until_this_weekday(3)), True],
   'fri': ['friday', 'Friday', lambda: TaskDate(days_until_this_weekday(4)), True],
   'sat': ['saturday', 'Saturday', lambda: TaskDate(days_until_this_weekday(5)), True],
   'sun': ['sunday', 'Sunday', lambda: TaskDate(days_until_this_weekday(6)), True],
   'tod': ['today', 'today', lambda: TaskDate(0), True],
   'now': ['now', 'today', lambda: TaskDate(0), True],
   'tom': ['tomorrow', 'tomorrow', lambda: TaskDate(1), True],
   'yes': ['yesterday', 'yesterday', lambda: TaskDate(-1), True],
   'nex': ['next week', 'next week', lambda: TaskDate(7), True],
   'soo': ['soon', 'soon', lambda: TaskDate(TaskDate.SOON), True],
   'fut': ['future', 'in the future', lambda: TaskDate(TaskDate.FUTURE), True],
   'lat': ['later', 'in the future', lambda: TaskDate(TaskDate.FUTURE), True],
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
