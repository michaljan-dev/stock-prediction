from app import db, app
from .models import SchedulerEntry, CrontabSchedule
import datetime


@app.route("/periodic")
def periodic():
    dse = SchedulerEntry()
    dse.name = "sinet.core.test.tik"
    dse.task = "sinet.core.test.tik"
    dse.enabled = True

    # schudule task to run after 30 seconds
    dtime = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)

    # interval
    period = 8
    frequency = "seconds"

    crontab = CrontabSchedule()
    crontab.day_of_month = dtime.day
    crontab.hour = dtime.hour
    crontab.minute = dtime.minute
    crontab.month_of_year = dtime.month
    dse.args = [2, 8]
    dse.kwargs = dict(period=period, frequency=frequency, taskname="multiply")
    dse.crontab = crontab

    # add entry to db
    db.session.add(crontab)
    db.session.add(dse)
    db.session.commit()
    return (
        "Task successfully scheduled to run on %s with frequency period of %d seconds"
        % (dtime, period)
    )
