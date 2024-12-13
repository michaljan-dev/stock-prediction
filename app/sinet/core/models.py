from app import db
from celery import schedules
import datetime
import json
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class Module(Base):
    __tablename__ = "module"

    name = db.Column(db.String(225), nullable=False, unique=True)
    version = db.Column(db.String(225), nullable=False, unique=True)

    # New instance instantiation procedure
    def __init__(self, name, module):

        self.name = name
        self.version = module


# dynamic config variables
class Config(Base):
    __tablename__ = "config"

    scope = db.Column(db.String(20), nullable=False, index=True)
    key = db.Column(db.String(225), nullable=False, index=True)
    value = db.Column(db.Text(), nullable=False)

    # New instance instantiation procedure
    def __init__(self, scope, key, value):

        self.scope = scope
        self.key = key
        self.value = value


# Cron - celery


class CrontabSchedule(Base):
    __tablename__ = "celery_crontabs"

    minute = db.Column(db.String(64), default="*")
    hour = db.Column(db.String(64), default="*")
    day_of_week = db.Column(db.String(64), default="*")
    day_of_month = db.Column(db.String(64), default="*")
    month_of_year = db.Column(db.String(64), default="*")

    @property
    def schedule(self):
        return schedules.crontab(
            minute=self.minute,
            hour=self.hour,
            day_of_week=self.day_of_week,
            day_of_month=self.day_of_month,
            month_of_year=self.month_of_year,
        )

    @classmethod
    def from_schedule(cls, dbsession, schedule):
        spec = {
            "minute": schedule._orig_minute,
            "hour": schedule._orig_hour,
            "day_of_week": schedule._orig_day_of_week,
            "day_of_month": schedule._orig_day_of_month,
            "month_of_year": schedule._orig_month_of_year,
        }
        try:
            query = dbsession.query(CrontabSchedule)
            query = query.filter_by(**spec)
            existing = query.one()
            return existing
        except NoResultFound:
            return cls(**spec)
        except MultipleResultsFound:
            query = dbsession.query(CrontabSchedule)
            query = query.filter_by(**spec)
            query.delete()
            dbsession.commit()
            return cls(**spec)


class IntervalSchedule(Base):
    __tablename__ = "celery_intervals"

    every = Column(Integer, nullable=False)
    period = Column(String(24))

    @property
    def schedule(self):
        return schedules.schedule(datetime.timedelta(**{self.period: self.every}))

    @classmethod
    def from_schedule(cls, dbsession, schedule, period="seconds"):
        every = max(schedule.run_every.total_seconds(), 0)
        try:
            query = dbsession.query(IntervalSchedule)
            query = query.filter_by(every=every, period=period)
            existing = query.one()
            return existing
        except NoResultFound:
            return cls(every=every, period=period)
        except MultipleResultsFound:
            query = dbsession.query(IntervalSchedule)
            query = query.filter_by(every=every, period=period)
            query.delete()
            dbsession.commit()
            return cls(every=every, period=period)


class SchedulerEntry(Base):
    __tablename__ = "celery_schedules"

    name = Column(String(255))
    task = Column(String(255))
    interval_id = Column(Integer, ForeignKey("celery_intervals.id"))
    crontab_id = Column(Integer, ForeignKey("celery_crontabs.id"))
    arguments = Column(String(255), default="[]")
    keyword_arguments = Column(String(255), default="{}")
    queue = Column(String(255))
    exchange = Column(String(255))
    routing_key = Column(String(255))
    expires = Column(DateTime)
    enabled = Column(Boolean, default=True)
    last_run_at = Column(DateTime)
    total_run_count = Column(Integer, default=0)
    date_changed = Column(DateTime)

    interval = relationship(IntervalSchedule)
    crontab = relationship(CrontabSchedule)

    @property
    def args(self):
        return json.loads(self.arguments)

    @args.setter
    def args(self, value):
        self.arguments = json.dumps(value)

    @property
    def kwargs(self):
        return json.loads(self.keyword_arguments)

    @kwargs.setter
    def kwargs(self, kwargs_):
        self.keyword_arguments = json.dumps(kwargs_)

    @property
    def schedule(self):
        if self.interval:
            return self.interval.schedule
        if self.crontab:
            return self.crontab.schedule


@db.event.listens_for(SchedulerEntry, "before_insert")
def _set_entry_changed_date(mapper, connection, target):
    target.date_changed = datetime.datetime.utcnow()
