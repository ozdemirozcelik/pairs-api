import re
from typing import Dict, List  # for type hinting
from db import db
from datetime import datetime
from sqlalchemy.sql import (
    func,
)  # 'sqlalchemy' is being installed together with 'flask-sqlalchemy'


AccountJSON = Dict[str, float]  # custom type hint


class AccountModel(db.Model):
    __tablename__ = "account"

    rowid = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )  # using 'rowid' as the default key
    timestamp = db.Column(
        db.DateTime(timezone=False),
        # server_default=func.timezone("UTC", func.current_timestamp()) # this can be problematic for sqlite3
        server_default=func.current_timestamp()  # TODO: check for sqlite3 and postgres
        # db.DateTime(timezone=False), server_default = func.now()
    )  # DATETIME DEFAULT (CURRENT_TIMESTAMP) for sqlite3
    AvailableFunds = db.Column(db.Float)
    BuyingPower = db.Column(db.Float)
    DailyPnL = db.Column(db.Float)
    GrossPositionValue = db.Column(db.Float)
    MaintMarginReq = db.Column(db.Float)
    NetLiquidation = db.Column(db.Float)
    RealizedPnL = db.Column(db.Float)
    UnrealizedPnL = db.Column(db.Float)

    def __init__(
        self,
        timestamp: datetime,
        AvailableFunds: float,
        BuyingPower: float,
        DailyPnL: float,
        GrossPositionValue: float,
        MaintMarginReq: float,
        NetLiquidation: float,
        RealizedPnL: float,
        UnrealizedPnL: float,
    ):
        self.timestamp = timestamp
        self.AvailableFunds = AvailableFunds
        self.BuyingPower = BuyingPower
        self.DailyPnL = DailyPnL
        self.GrossPositionValue = GrossPositionValue
        self.MaintMarginReq = MaintMarginReq
        self.NetLiquidation = NetLiquidation
        self.RealizedPnL = RealizedPnL
        self.UnrealizedPnL = UnrealizedPnL

    def json(self) -> AccountJSON:
        return {
            "rowid": self.rowid,
            "timestamp": str(self.timestamp),
            "AvailableFunds": self.AvailableFunds,
            "BuyingPower": self.BuyingPower,
            "DailyPnL": self.DailyPnL,
            "GrossPositionValue": self.GrossPositionValue,
            "MaintMarginReq": self.MaintMarginReq,
            "NetLiquidation": self.NetLiquidation,
            "RealizedPnL": self.RealizedPnL,
            "UnrealizedPnL": self.UnrealizedPnL,
        }

    @classmethod
    def find_by_rowid(cls, rowid) -> "AccountModel":

        return cls.query.filter_by(rowid=rowid).first()

    def insert(self) -> None:

        db.session.add(self)
        db.session.commit()

    def update(self, rowid) -> None:

        item_to_update = self.query.filter_by(rowid=rowid).first()

        item_to_update.timestamp = self.timestamp
        item_to_update.AvailableFunds = self.AvailableFunds
        item_to_update.BuyingPower = self.BuyingPower
        item_to_update.DailyPnL = self.DailyPnL
        item_to_update.GrossPositionValue = self.GrossPositionValue
        item_to_update.MaintMarginReq = self.MaintMarginReq
        item_to_update.NetLiquidation = self.NetLiquidation
        item_to_update.RealizedPnL = self.RealizedPnL
        item_to_update.UnrealizedPnL = self.UnrealizedPnL

        db.session.commit()

    @classmethod
    def get_rows(cls, number_of_items) -> List:

        if number_of_items == "0":
            # return cls.query.order_by(desc("rowid")).all() # needs from sqlalchemy import desc
            return cls.query.order_by(cls.rowid.desc())  # better, no need to import
        else:
            return cls.query.order_by(cls.rowid.desc()).limit(number_of_items)

    def delete(self) -> None:

        db.session.delete(self)
        db.session.commit()

    # TODO: add a find_by_date function
    # def find_by_date(cls, date) -> "AccountModel":
    #
    #     return cls.query.filter_by(cls.timestamp == date).first()
