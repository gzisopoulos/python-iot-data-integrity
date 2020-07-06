from app import db
from app.models.base import BaseModel


class EventFormat(BaseModel):
    event_code = db.Column(db.Integer, unique=True, index=True)
    event_description = db.Column(db.String(80))

    @classmethod
    def find_by_event_code(cls, event_code):
        return cls.query.filter_by(event_code=event_code).first()
