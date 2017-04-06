from config import AUTO_ARCHIVE_MIN_DURATION, AUTO_ARCHIVE_MAX_DURATION, AUTO_ARCHIVE_END_TIME_HOUR, AUTO_ARCHIVE_MAX_NUM_ASSETS, AUTO_ARCHIVE_END_TIME_MINUTE
from build_all_tables import FilesDropped, db_session
from interplay_api import submit_for_archive, cancel_job_if_pending
from datetime import datetime
from time import sleep


def archive():  # Auto Archiving service
    # get files that need archiving
    db_result = db_session.query(FilesDropped).filter(
        FilesDropped.date_archived.is_(None),
        FilesDropped.date_removed.is_(None),
        FilesDropped.duration >= AUTO_ARCHIVE_MIN_DURATION.total_seconds()
    )
    # set some counters
    total_duration_archived = 0  # length of all assets queued for archive
    total_scheduled = 0  # number of assets queued for archive
    total_unscheduled = 0
    total_submitted_timeout = 0  # number of requests sent to the archive engine
    jobs_this_session = []
    for result in db_result:
        d = submit_for_archive(result)
        result.date_scheduled = datetime.utcnow()
        if d < 0:  # error when attempting to archive
            result.date_removed = datetime.utcnow()  # it was probably deleted move on
            total_submitted_timeout += 1
            total_unscheduled += 1
            if total_submitted_timeout >= 20:
                sleep(30)  # wait a minute after submitting 20 requests to avoid limit errors
                total_submitted_timeout = 0  # reset
            print(result.mob_id + ' Could not be archived!')
        elif d == 0:  # already archived
            result.date_archived = datetime.utcnow()
        else:  # archive successful
            total_duration_archived += result.duration
            total_submitted_timeout += 1
            total_scheduled += 1
            jobs_this_session.append(result)
            print('Submitted ' + result.mob_id + ' for archive at ' + str(datetime.utcnow()))
            if total_submitted_timeout >= 20:
                sleep(60)  # wait a minute after submitting 20 requests to avoid limit errors
                total_submitted_timeout = 0  # reset
        db_session.commit()
        # did we reach our quota
        if datetime.today().hour >= AUTO_ARCHIVE_END_TIME_HOUR and datetime.today().minute >= AUTO_ARCHIVE_END_TIME_MINUTE:
                # or total_duration_archived/3600 > AUTO_ARCHIVE_MAX_DURATION \
                # or total_scheduled >= AUTO_ARCHIVE_MAX_NUM_ASSETS:
            if datetime.today().hour >= AUTO_ARCHIVE_END_TIME_HOUR and datetime.today().minute >= AUTO_ARCHIVE_END_TIME_MINUTE:  # cancel jobs still pending
                for job in jobs_this_session:
                    cancel_job_if_pending(job)
                db_session.commit()
            print('duration sent to archive ' + str(total_duration_archived/3600) + ' hours')
            print('duration scheduled ' + str(total_scheduled))
            return
