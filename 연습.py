import datetime

today = datetime.datetime.now()
date = str(today.year) + str(today.month) + str(today.day)
today += datetime.timedelta(days=7)
to = str(today.year) + str(today.month) + str(today.day)
print(date)
print(to)