from typing import Dict, List, Union  # for type hinting
from db import db

PairJSON = Dict[str, Union[str, float, int]]  # custom type hint


class PairModel(db.Model):
    __tablename__ = "pairs"

    # sqlalchemy needs a primary key (either dummy or real)
    rowid = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )  # using 'rowid' as the default key
    name = db.Column(db.String(81), unique=True)
    ticker1 = db.Column(db.String(51))
    ticker2 = db.Column(db.String(51))
    hedge = db.Column(db.Float(precision=8))
    status = db.Column(db.Integer)
    notes = db.Column(db.String)

    def __init__(
        self,
        name: str,
        ticker1: str,
        ticker2: str,
        hedge: float,
        status: int,
        notes: str,
    ):
        self.name = name
        self.hedge = hedge
        self.status = status
        self.ticker1 = ticker1
        self.ticker2 = ticker2
        self.notes = notes

    def json(self) -> PairJSON:
        return {
            "name": self.name,
            "ticker1": self.ticker1,
            "ticker2": self.ticker2,
            "hedge": self.hedge,
            "status": self.status,
            "notes": self.notes,
        }

    @classmethod
    def find_by_name(cls, name: str) -> "PairModel":

        return cls.query.filter_by(name=name).first()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:
        #
        # connection = sqlite3.connect('data.db', timeout=10)
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "SELECT * FROM {table} WHERE name=?".format(table=TABLE_PAIRS)
        #     cursor.execute(query, (name,))
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
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "INSERT INTO {table} VALUES(?, ?, ?)".format(table=TABLE_PAIRS)
        #
        #     cursor.execute(query, (self.name, self.hedge, self.status))
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

    def update(self) -> None:

        item_to_update = self.query.filter_by(name=self.name).first()

        item_to_update.hedge = self.hedge
        item_to_update.status = self.status
        item_to_update.notes = self.notes

        db.session.commit()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # connection = sqlite3.connect('data.db')
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "UPDATE {table} SET hedge=?, status=? WHERE name=?".format(table=TABLE_PAIRS)
        #
        #     cursor.execute(query, (self.hedge, self.status, self.name))
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
    def get_rows(cls, number_of_items) -> List:

        if number_of_items == "0":
            # return cls.query.order_by(desc("rowid")).all() # needs from sqlalchemy import desc
            return cls.query.order_by(cls.rowid.desc())  # better, no need to import
        else:
            return cls.query.order_by(cls.rowid.desc()).limit(number_of_items).all()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # if number_of_items == "0":
        #     query = "SELECT * FROM {table} ORDER BY rowid DESC".format(table=TABLE_PAIRS)
        # else:
        #     query = "SELECT * FROM {table} ORDER BY rowid DESC " \
        #             "LIMIT {number}".format(table=TABLE_PAIRS, number=number_of_items)
        #
        # connection = sqlite3.connect('data.db', timeout=10)
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
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "DELETE FROM {table} WHERE name=?".format(table=TABLE_PAIRS)
        #     cursor.execute(query, (name,))
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

    def combineticker(self) -> bool:

        # TODO: check for other special characters
        if ("-" in self.ticker1) or ("-" in self.ticker2):
            self.notes = "problematic ticker!"
            self.status = 0
            success_flag = False
        else:
            self.name = self.ticker1 + "-" + self.ticker2
            success_flag = True

        return success_flag

    @classmethod
    def find_active_ticker(cls, ticker: str) -> "PairModel":

        return cls.query.filter(
            ((cls.ticker1 == ticker) | (cls.ticker2 == ticker)) & (cls.status == 1)
        ).first()

    @classmethod
    def get_active_pairs(cls, number_of_items: str) -> List:

        if number_of_items == "0":
            return cls.query.filter(cls.status == 1)
        else:
            return cls.query.filter(cls.status == 1).limit(number_of_items).all()
