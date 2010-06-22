# provides way to swap out datetime for testing

from datetime import datetime, timedelta

def now():
    return datetime.today() + timedelta(hours=0, minutes=0)
