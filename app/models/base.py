from app import db


class BaseModel(db.Model):
    # __tablename__ = None
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def get_id(self):
        return self.id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        ß
