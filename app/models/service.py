from app import db
from app.models.base import BaseModel


class Service(BaseModel):
    __tablename__ = 'service'

    name = db.Column(db.String(20), nullable=False)
    port = db.Column(db.Integer, index=True, unique=True, nullable=False)
    ip_address = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Service {}>'.format(self.name)

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_port(cls, port):
        return cls.query.filter_by(port=port).first()
