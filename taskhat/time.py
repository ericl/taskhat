# provides way to swap out datetime for testing

from datetime import datetime, timedelta

def now():
#    return datetime.today() + timedelta(days=0, hours=0, minutes=0)
    return datetime.today()

def make_time(*args, **kwargs):
    return datetime(*args, **kwargs)

def make_timedelta(*args, **kwargs):
    return timedelta(*args, **kwargs)
