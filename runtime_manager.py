from db_schedule_tasks import update_db
from archive_schedule_tasks import archive
import time
import datetime
from config import AUTO_ARCHIVE_START_TIME_HOUR, AUTO_ARCHIVE_START_TIME_MINUTE, AUTO_ARCHIVE_END_TIME_HOUR, AUTO_ARCHIVE_END_TIME_MINUTE

# if for some reason this script is still running
# after 3 days, we'll stop after
# todo make this a while true

for i in range(0, 4):
    # sleep until 2AM or whatever time the config says
    t = datetime.datetime.today()  # what time is it now
    future = datetime.datetime(t.year, t.month, t.day, AUTO_ARCHIVE_START_TIME_HOUR, AUTO_ARCHIVE_START_TIME_MINUTE) # what time do we want to start
    if t.hour >= AUTO_ARCHIVE_START_TIME_HOUR:  # if the start time is in the past make it for tomorrow
        if t.hour == AUTO_ARCHIVE_START_TIME_HOUR and t.minute < AUTO_ARCHIVE_START_TIME_MINUTE:
            pass
        else:
            future += datetime.timedelta(days=1)
    print('Sleeping until ' + str(future))
    time.sleep((future-t).seconds)  # Nap Time!
    # Beep! Beep! Beep! Wake Up, Time For Work!
    AUTO_ARCHIVE_START_TIME = datetime.datetime.today()
    if AUTO_ARCHIVE_START_TIME_HOUR <= AUTO_ARCHIVE_END_TIME_HOUR:
        if AUTO_ARCHIVE_START_TIME_HOUR == AUTO_ARCHIVE_END_TIME_HOUR and AUTO_ARCHIVE_START_TIME_MINUTE >= AUTO_ARCHIVE_END_TIME_MINUTE:
            AUTO_ARCHIVE_END_TIME = datetime.datetime(
                AUTO_ARCHIVE_START_TIME.year,
                AUTO_ARCHIVE_START_TIME.month,
                AUTO_ARCHIVE_START_TIME.day + 1,
                AUTO_ARCHIVE_END_TIME_HOUR,
                AUTO_ARCHIVE_END_TIME_MINUTE
            )
        else:
            AUTO_ARCHIVE_END_TIME = datetime.datetime(
                AUTO_ARCHIVE_START_TIME.year,
                AUTO_ARCHIVE_START_TIME.month,
                AUTO_ARCHIVE_START_TIME.day,
                AUTO_ARCHIVE_END_TIME_HOUR,
                AUTO_ARCHIVE_END_TIME_MINUTE
            )
    else:
        AUTO_ARCHIVE_END_TIME = datetime.datetime(
            AUTO_ARCHIVE_START_TIME.year,
            AUTO_ARCHIVE_START_TIME.month,
            AUTO_ARCHIVE_START_TIME.day + 1,
            AUTO_ARCHIVE_END_TIME_HOUR,
            AUTO_ARCHIVE_END_TIME_MINUTE
        )
    print('Starting Database Update')
    update_db()
    print('DB Updated Starting Archive Service')
    archive(AUTO_ARCHIVE_START_TIME, AUTO_ARCHIVE_END_TIME)
    print('Finished Archive at ' + str(datetime.datetime.today()))
