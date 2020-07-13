from sqlalchemy import func

from app import app, db
from app.models.base import BaseModel


class Event(BaseModel):
    """
    All device signals and fields are stored inside this model.
    In real-world example this will be the most crucial table of your database.
    We prefer to include it in its own database.

    Note that our fields are verbose in order to understand them. It is a bad
    practice to keep them that way.
    """
    __bind_key__ = 'ingest_db'

    device_number = db.Column(db.String, index=True)
    event_code = db.Column(db.String, index=True)
    message_date = db.Column(db.DateTime, index=True)
    latitude = db.Column(db.Numeric(precision=8, scale=6), default=0)
    longitude = db.Column(db.Numeric(precision=8, scale=6), default=0)

    @classmethod
    def get_count(cls):
        """
        Returns count query for class
        """
        count_query = cls.query.statement.with_only_columns([func.count()]).order_by(None)
        count = db.session.execute(count_query).scalar()
        return count

    @classmethod
    def get_randomized_set(cls, count):
        """
        Returns a list of randomized events.
        """
        randomized_set = cls.query.order_by(func.random()).limit(
            int(count) / int(app.config['RANDOMIZED_SET_SCALE'])).all()
        return randomized_set

    @classmethod
    async def get_time_filtered_events(cls, time_period):
        """
        Returns a list of events for a specific period of time.
        """
        return cls.query.filter(cls.message_date > time_period).all()
