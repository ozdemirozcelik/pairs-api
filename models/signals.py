from typing import Dict, Union  # for type hinting
from db import db
from sqlalchemy.sql import (
    func,
)  # 'sqlalchemy' is being installed together with 'flask-sqlalchemy'

SignalJSON = Dict[str, Union[str, float, int]]  # custom type hint

PASSPHRASE = "webhook"  # Passphrase is required to register webhooks


class SignalModel(db.Model):
    __tablename__ = "signals"

    rowid = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )  # using 'rowid' as the default key
    timestamp = db.Column(
        db.DateTime(timezone=True), server_default=func.now()
    )  # DATETIME DEFAULT (CURRENT_TIMESTAMP)
    ticker = db.Column(db.String)
    order_action = db.Column(db.String)
    order_contracts = db.Column(db.Integer)
    order_price = db.Column(db.Float)
    mar_pos = db.Column(db.String)
    mar_pos_size = db.Column(db.Integer)
    pre_mar_pos = db.Column(db.String)
    pre_mar_pos_size = db.Column(db.Integer)
    order_comment = db.Column(db.String)
    order_status = db.Column(db.String)

    def __init__(
        self,
        ticker: str,
        order_action: str,
        order_contracts: int,
        order_price: float,
        mar_pos: str,
        mar_pos_size: int,
        pre_mar_pos: str,
        pre_mar_pos_size: int,
        order_comment: str,
        order_status: str,
    ):
        self.ticker = ticker
        self.order_action = order_action
        self.order_contracts = order_contracts
        self.order_price = order_price
        self.mar_pos = mar_pos
        self.mar_pos_size = mar_pos_size
        self.pre_mar_pos = pre_mar_pos
        self.pre_mar_pos_size = pre_mar_pos_size
        self.order_comment = order_comment
        self.order_status = order_status

    def json(self) -> SignalJSON:
        return {
            "rowid": self.rowid,
            "timestamp": str(self.timestamp),
            "ticker": self.ticker,
            "order_action": self.order_action,
            "order_contracts": self.order_contracts,
            "order_price": self.order_price,
            "mar_pos": self.mar_pos,
            "mar_pos_size": self.mar_pos_size,
            "pre_mar_pos": self.pre_mar_pos,
            "pre_mar_pos_size": self.pre_mar_pos_size,
            "order_comment": self.order_comment,
            "order_status": self.order_status,
        }

    @staticmethod
    def passphrase_wrong(passphrase) -> bool:
        if passphrase == PASSPHRASE:
            return False
        return True

    @classmethod
    def find_by_rowid(cls, rowid) -> "SignalModel":

        return cls.query.filter_by(rowid=rowid).first()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # if rowid == 0:
        #     return None
        #
        # connection = sqlite3.connect('data.db', timeout=10)
        #
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "SELECT rowid, * FROM {table} WHERE rowid=?".format(table=TABLE_SIGNALS)
        #     cursor.execute(query, (rowid,))
        #     row = cursor.fetchone()
        #
        # except sqlite3.Error as e:
        #     print('Database error occurred - ', e)
        #     raise
        #
        # finally:
        #     if connection:
        #         connection.close()
        #
        # if row:
        #     return cls(*row)
        #
        # return None

    def insert(self) -> None:

        db.session.add(self)
        db.session.commit()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # connection = sqlite3.connect('data.db', timeout=10)
        #
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "INSERT INTO {table} (ticker, order_action, order_contracts, order_price," \
        #             "mar_pos, mar_pos_size, pre_mar_pos, pre_mar_pos_size, order_comment, order_status) " \
        #             "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(table=TABLE_SIGNALS)
        #
        #     cursor.execute(query, (self.ticker, self.order_action, self.order_contracts, self.order_price,
        #                            self.mar_pos, self.mar_pos_size, self.pre_mar_pos, self.pre_mar_pos_size,
        #                            self.order_comment, self.order_status))
        #
        #     connection.commit()
        #
        # except sqlite3.Error as e:  # handling the exception with generic SQL error code
        #     print('Database error occurred - ', e)  # better to log the error
        #     raise
        #
        # finally:
        #     if connection:
        #         connection.close()  # disconnect the database even if exception occurs

    def update(self, rowid) -> None:

        item_to_update = self.query.filter_by(rowid=rowid).first()

        item_to_update.ticker = self.ticker
        item_to_update.order_action = self.order_action
        item_to_update.order_contracts = self.order_contracts
        item_to_update.order_price = self.order_price
        item_to_update.mar_pos = self.mar_pos
        item_to_update.mar_pos_size = self.mar_pos_size
        item_to_update.pre_mar_pos = self.pre_mar_pos
        item_to_update.pre_mar_pos_size = self.pre_mar_pos_size
        item_to_update.order_comment = self.order_comment
        item_to_update.order_status = self.order_status

        db.session.commit()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # connection = sqlite3.connect('data.db')
        #
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "UPDATE {table} SET ticker=?, order_action=?, order_contracts=?,order_price=?," \
        #             "mar_pos=?, mar_pos_size=?, pre_mar_pos=?, pre_mar_pos_size=?, order_comment=?, order_status=? " \
        #             "WHERE rowid=?".format(table=TABLE_SIGNALS)
        #
        #     cursor.execute(query, (self.ticker, self.order_action, self.order_contracts, self.order_price,
        #                            self.mar_pos, self.mar_pos_size, self.pre_mar_pos, self.pre_mar_pos_size,
        #                            self.order_comment, self.order_status, rowid))
        #
        #     connection.commit()
        #
        # except sqlite3.Error as e:
        #     print('Database error occurred - ', e)
        #     raise
        #
        # finally:
        #     if connection:
        #         connection.close()

    @classmethod
    def get_rows(cls, number_of_items) -> "SignalModel":

        if number_of_items == "0":
            # return cls.query.order_by(desc("rowid")).all() # needs from sqlalchemy import desc
            return cls.query.order_by(cls.rowid.desc())  # better, no need to import
        else:
            return cls.query.order_by(cls.rowid.desc()).limit(number_of_items).all()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # if number_of_items == "0":
        #     query = "SELECT rowid, * FROM {table} ORDER BY rowid DESC".format(table=TABLE_SIGNALS)
        # else:
        #     query = "SELECT rowid, * FROM {table} ORDER BY rowid DESC " \
        #             "LIMIT {number}".format(table=TABLE_SIGNALS, number=number_of_items)
        #
        # connection = sqlite3.connect('data.db', timeout=10)
        #
        # try:
        #     cursor = connection.cursor()
        #
        #     cursor.execute(query)
        #
        #     result = cursor.fetchall()  # Keep the result in memory after closing the database
        #
        # except sqlite3.Error as e:
        #     print('Database error occurred - ', e)
        #     raise
        #
        # finally:
        #     if connection:
        #         connection.close()
        #
        # items = []
        #
        # for row in result:
        #     items.append(cls(*row))
        #
        # return items

    def delete(self) -> None:

        db.session.delete(self)
        db.session.commit()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # connection = sqlite3.connect('data.db', timeout=10)
        #
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "DELETE FROM {table} WHERE rowid=?".format(table=TABLE_SIGNALS)
        #     cursor.execute(query, (rowid,))
        #
        #     connection.commit()
        #
        # except sqlite3.Error as e:
        #     print('Database error occurred - ', e)
        #     raise
        #
        # finally:
        #     if connection:
        #         connection.close()
