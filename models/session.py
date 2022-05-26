from typing import Dict, Union  # for type hinting
from db import db
from sqlalchemy.sql import func
from datetime import datetime
import pytz

UserJSON = Dict[str, str]  # custom type hint


class SessionModel(db.Model):
    __tablename__ = "simplesession"

    # sqlalchemy needs a primary key (either dummy or real)
    rowid = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )  # using 'rowid' as the default key
    value = db.Column(db.String(80), unique=True)
    expiry = db.Column(
        db.DateTime(timezone=False),
        server_default=func.timezone("UTC", func.current_timestamp()),
    )

    def __init__(self, value: str, expiry: datetime):
        self.value = value
        self.expiry = expiry

    def json(self) -> UserJSON:
        return {"value": self.value}

    @classmethod
    def find_by_value(cls, value) -> "SessionModel":

        return cls.query.filter_by(value=value).first()

    def insert(self) -> None:

        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def delete_all() -> None:
        try:
            db.session.query(SessionModel).delete()
            db.session.commit()
        except:
            db.session.rollback()

    @classmethod
    def delete_expired(cls) -> None:

        date_now = datetime.now(tz=pytz.utc)

        print(date_now)

        try:
            cls.query.filter(cls.expiry < date_now).delete()
            db.session.commit()
        except:
            db.session.rollback()
