from task import TaskDate

from utime import days_until_this_weekday
import os

# run_in_background: don't quit with window close
#   - enables fast startup
#   - may not play nice with wm focus prevention
# show_recurring_events: show daily schedule and such in main window
CONFIG = {'run_in_background': True,
          'show_recurring_events': True}

configfile = os.path.expanduser('~/.taskhat')
if os.path.exists(configfile):
    try:
        CONFIG.update(eval(open(configfile).read()))
        print "Read config from file:", CONFIG
    except Exception, e:
        print "Error reading config:", e

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
