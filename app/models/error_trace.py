from app import db
from app.models.base import BaseModel


class ErrorTrace(BaseModel):
    __tablename__ = 'error_trace'

    device_number = db.Column(db.String(20), index=True, unique=True, nullable=False)
    error_code = db.Column(db.Integer, index=True, unique=True, nullable=False)
    event_code = db.Column(db.String(10), nullable=False)
    message_date = db.Column(db.DateTime)

    def __repr__(self):
        return '<Error Trace {}>'.format(self.id)

    @classmethod
    def find_by_error_code(cls, error_code):
        return cls.query.filter_by(error_code=error_code).all()

    @classmethod
    def find_by_device_id(cls, device_id):
        return cls.query.filter_by(device_id=device_id).all()
