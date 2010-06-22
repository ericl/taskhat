# provides way to swap out datetime for testing

from datetime import datetime, timedelta

def now():
#    return datetime.today() + timedelta(days=0, hours=0, minutes=0)
    return datetime.today()

def make_time(*args):
    return datetime(*args)

def make_timedelta(*args):
    return timedelta(*args)
