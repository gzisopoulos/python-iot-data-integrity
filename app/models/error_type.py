from app import db
from app.models.base import BaseModel


class ErrorType(BaseModel):
    __tablename__ = 'error_type'

    error_code = db.Column(db.Integer, index=True, unique=True, nullable=False)
    description = db.Column(db.String(20))
    limit = db.Column(db.Integer(), nullable=False, server_default='1')
    critical = db.Column(db.SmallInteger, nullable=False, server_default='0')

    def __repr__(self):
        return '<Error Type {}>'.format(self.error_code)

    @classmethod
    def find_by_error_code(cls, error_code):
        return cls.query.filter_by(error_code=error_code).first()

    @classmethod
    def find_critical(cls):
        return cls.query.filter_by(critical=1).all()

    def is_critical(self):
        return self.critical
