import re
from typing import Dict, List, Union  # for type hinting
from db import db
from datetime import datetime
from sqlalchemy.sql import (
    func,
)  # 'sqlalchemy' is being installed together with 'flask-sqlalchemy'

from models.pairs import PairModel
from models.tickers import TickerModel

SignalJSON = Dict[str, Union[str, float, int]]  # custom type hint

PASSPHRASE = "webhook"  # Passphrase is required to register webhooks


class SignalModel(db.Model):
    __tablename__ = "signals"

    rowid = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )  # using 'rowid' as the default key
    timestamp = db.Column(
        db.DateTime(timezone=False),
        # server_default=func.timezone("UTC", func.current_timestamp()) # this can be problematic for sqlite3
        server_default=func.current_timestamp()  # TODO: check for sqlite3 and postgres
        # db.DateTime(timezone=False), server_default = func.now()
    )  # DATETIME DEFAULT (CURRENT_TIMESTAMP) for sqlite3
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

    # Columns needed for order creation
    ticker_type = db.Column(db.String)
    ticker1 = db.Column(db.String)
    ticker2 = db.Column(db.String)
    hedge_param = db.Column(db.Float)
    order_id1 = db.Column(db.Integer)
    order_id2 = db.Column(db.Integer)
    price1 = db.Column(db.Float)
    price2 = db.Column(db.Float)
    fill_price = db.Column(db.Float)
    slip = db.Column(db.Float)
    error_msg = db.Column(db.String)
    status_msg = db.Column(db.String)

    def __init__(
        self,
        timestamp: datetime,
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
        ticker_type: str,
        ticker1: str,
        ticker2: str,
        hedge_param: float,
        order_id1: int,
        order_id2: int,
        price1: float,
        price2: float,
        fill_price: float,
        slip: float,
        error_msg: str,
        status_msg: str,
    ):
        self.timestamp = timestamp
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
        self.ticker_type = ticker_type
        self.ticker1 = ticker1
        self.ticker2 = ticker2
        self.hedge_param = hedge_param
        self.order_id1 = order_id1
        self.order_id2 = order_id2
        self.price1 = price1
        self.price2 = price2
        self.fill_price = fill_price
        self.slip = slip
        self.error_msg = error_msg
        self.status_msg = status_msg

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
            "ticker_type": self.ticker_type,
            "ticker1": self.ticker1,
            "ticker2": self.ticker2,
            "hedge_param": self.hedge_param,
            "order_id1": self.order_id1,
            "order_id2": self.order_id2,
            "price1": self.price1,
            "price2": self.price2,
            "fill_price": self.fill_price,
            "slip": self.slip,
            "error_msg": self.error_msg,
            "status_msg": self.status_msg,
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
        item_to_update.timestamp = self.timestamp
        item_to_update.order_action = self.order_action
        item_to_update.order_contracts = self.order_contracts
        item_to_update.order_price = self.order_price
        item_to_update.mar_pos = self.mar_pos
        item_to_update.mar_pos_size = self.mar_pos_size
        item_to_update.pre_mar_pos = self.pre_mar_pos
        item_to_update.pre_mar_pos_size = self.pre_mar_pos_size
        item_to_update.order_comment = self.order_comment
        item_to_update.order_status = self.order_status
        item_to_update.ticker_type = self.ticker_type
        item_to_update.ticker1 = self.ticker1
        item_to_update.ticker2 = self.ticker2
        item_to_update.hedge_param = self.hedge_param
        item_to_update.order_id1 = self.order_id1
        item_to_update.order_id2 = self.order_id2
        item_to_update.price1 = self.price1
        item_to_update.price2 = self.price2
        item_to_update.fill_price = self.fill_price
        item_to_update.slip = self.slip
        item_to_update.error_msg = self.error_msg
        item_to_update.status_msg = self.status_msg

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
    def get_rows(cls, number_of_items) -> List:

        if number_of_items == "0":
            # return cls.query.order_by(desc("rowid")).all() # needs from sqlalchemy import desc
            return cls.query.order_by(cls.rowid.desc())  # better, no need to import
        else:
            return cls.query.order_by(cls.rowid.desc()).limit(number_of_items)

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

    @classmethod
    def get_list_ticker(cls, ticker_name, number_of_items) -> List:

        pair = False

        tickers = ticker_name.split("-")  # check if pair or single
        ticker1 = tickers[0]
        ticker2 = ""
        if len(tickers) == 2:
            ticker2 = tickers[1]
            pair = True

        if number_of_items == "0":
            if pair:
                return (
                    cls.query.filter(
                        (cls.ticker1 == ticker1) & (cls.ticker2 == ticker2)
                    )
                    .order_by(cls.rowid.desc())
                    .all()
                )
            else:
                return (
                    cls.query.filter(cls.ticker1 == ticker1)
                    .filter(cls.ticker_type == "single")
                    .order_by(cls.rowid.desc())
                    .all()
                )
        else:
            if pair:
                return (
                    cls.query.filter(
                        (cls.ticker1 == ticker1) & (cls.ticker2 == ticker2)
                    )
                    .order_by(cls.rowid.desc())
                    .limit(number_of_items)
                )
            else:
                return (
                    cls.query.filter(cls.ticker1 == ticker1)
                    .filter(cls.ticker_type == "single")
                    .order_by(cls.rowid.desc())
                    .limit(number_of_items)
                )

    @classmethod
    def get_list_ticker_dates(
        cls, ticker_name, number_of_items, start_date, end_date
    ) -> List:

        pair = False

        tickers = ticker_name.split("-")  # check if pair or single
        ticker1 = tickers[0]
        ticker2 = ""
        if len(tickers) == 2:
            ticker2 = tickers[1]
            pair = True

        if number_of_items == "0":
            if pair:
                return (
                    cls.query.filter(
                        (cls.ticker1 == ticker1)
                        & (cls.ticker2 == ticker2)
                        & (cls.timestamp <= end_date)
                        & (cls.timestamp >= start_date)
                    )
                    .order_by(cls.rowid.desc())
                    .all()
                )
            else:
                return (
                    cls.query.filter(
                        (cls.ticker1 == ticker1)
                        & (cls.timestamp <= end_date)
                        & (cls.timestamp >= start_date)
                    )
                    .filter(cls.ticker_type == "single")
                    .order_by(cls.rowid.desc())
                    .all()
                )
        else:
            if pair:
                return (
                    cls.query.filter(
                        (cls.ticker1 == ticker1)
                        & (cls.ticker2 == ticker2)
                        & (cls.timestamp <= end_date)
                        & (cls.timestamp >= start_date)
                    )
                    .order_by(cls.rowid.desc())
                    .limit(number_of_items)
                )
            else:
                return (
                    cls.query.filter(
                        (cls.ticker1 == ticker1)
                        & (cls.timestamp <= end_date)
                        & (cls.timestamp >= start_date)
                    )
                    .filter(cls.ticker_type == "single")
                    .order_by(cls.rowid.desc())
                    .limit(number_of_items)
                )

    @classmethod
    def get_list_status(cls, order_status, number_of_items) -> List:

        if number_of_items == "0":
            if order_status == "waiting":
                return (
                    cls.query.filter(
                        (cls.order_status == "waiting")
                        | (cls.order_status == "rerouted")
                    )
                    .order_by(cls.rowid.desc())
                    .all()
                )
            else:
                return (
                    cls.query.filter_by(order_status=order_status)
                    .order_by(cls.rowid.desc())
                    .all()
                )
        else:
            if order_status == "waiting":
                return (
                    cls.query.filter(
                        (cls.order_status == "waiting")
                        | (cls.order_status == "rerouted")
                    )
                    .order_by(cls.rowid.desc())
                    .limit(number_of_items)
                )
            else:
                return (
                    cls.query.filter_by(order_status=order_status)
                    .order_by(cls.rowid.desc())
                    .limit(number_of_items)
                )

    def check_ticker_status(self) -> bool:

        # check if ticker is registered and trade status is active
        if self.ticker_type == "pair":
            pair_name = self.ticker1 + "-" + self.ticker2
            pair = PairModel.find_by_name(pair_name)
            # check if pair exists
            if pair:
                # check trade status
                # if pair is not active set a static pair status (not possible to update)
                if not pair.status:
                    self.order_status = "canceled"
                    self.status_msg = "passive ticker"
                    return False
                if float(self.hedge_param) != float(pair.hedge):
                    self.order_status = "canceled"
                    self.status_msg = "wrong hedge"
                    return False

                # if registered and active ticker
                else:
                    return True
            else:
                self.order_status = "error"
                self.status_msg = "unknown ticker"
                return False

        else:
            ticker = TickerModel.find_by_symbol(self.ticker1)
            # check if ticker exists
            if ticker:
                # check trade status
                # if ticker is not active set a static pair status (not possible to update)
                if not ticker.active:
                    self.order_status = "canceled"
                    self.status_msg = "passive ticker"
                    return False
                else:
                    # if registered and active ticker
                    return True
            else:
                self.order_status = "error"
                self.status_msg = "unknown ticker"
                return False

    def splitticker(self,) -> bool:

        success_flag = True
        currency_match = True

        eq12 = self.ticker.split("-")  # check if pair or single
        # print(eq12)  # ['LNT', '1.25*NYSE:FTS']

        if len(eq12) <= 2:

            eq1_hedge = re.findall(
                r"[-+]?\d*\.\d+|\d+", eq12[0]
            )  # hedge constant for the 1st ticker
            # print("eq1_hedge: ", eq1_hedge)  # []

            if len(eq1_hedge) > 0:
                eq1 = eq12[0].replace(eq1_hedge[0], "")
            else:
                eq1 = eq12[0]  # LNT

            eq1 = eq1.replace("*", "")
            # print("eq1: ", eq1)  # LNT

            eq1_split = eq1.rsplit(":", maxsplit=1)
            eq1_ticker_almost = eq1_split[len(eq1_split) - 1]

            # print("eq1_split: ", eq1_split)  # ['LNT']
            # print("eq1_ticker_almost: ", eq1_ticker_almost)  # LNT

            # check if the ticker security type is CASH or CRYPTO
            item = TickerModel.find_by_symbol(eq1_ticker_almost)

            if item:
                if item.sectype == "CASH":
                    fx1 = eq1_ticker_almost[0:3]  # get the first 3 char # USD
                    fx2 = eq1_ticker_almost[-3:]  # get the last 3 char # CAD
                    ticker_pair1 = fx1 + "." + fx2

                    # TODO: improve validity check
                    # check if valid fx pair
                    if len(ticker_pair1) != 7:  # check if it is in USD.CAD format
                        success_flag = False
                    # check for currency mismatch
                    if fx2 != item.currency:
                        currency_match = False
                        success_flag = False

                elif item.sectype == "CRYPTO":
                    cry2 = eq1_ticker_almost[-3:]  # get last 3 char
                    ticker_pair1 = eq1_ticker_almost.replace(".", "")
                    cry1 = eq1_ticker_almost[
                        0 : (len(ticker_pair1) - 3)
                    ]  # get the first 3 char
                    ticker_pair1 = cry1 + "." + cry2

                    # TODO: improve validity check
                    # check if valid crypto pair, accepts only USD pairs
                    if cry2 != item.currency or cry2 != "USD":
                        currency_match = False
                        success_flag = False

                else:

                    if (
                        "." in eq1_ticker_almost
                    ):  # For Class A,B type tickers EXP: BF.A BF.B
                        ticker_pair1 = eq1_ticker_almost.replace(
                            ".", " "
                        )  # convert Tradingview -> IB format
                    else:
                        ticker_pair1 = "".join(
                            char for char in eq1_ticker_almost if char.isalnum()
                        )

                        if eq1_ticker_almost != ticker_pair1:
                            success_flag = False

            # print("ticker_pair1: ", ticker_pair1)  # LNT

            if len(eq1_hedge) != 0:
                if eq1_hedge[0] != 1:
                    success_flag = False

            # print("problem_flag_first: ", success_flag)

            self.ticker_type = "single"
            self.ticker1 = ticker_pair1

        if len(eq12) == 2:

            eq2_hedge = re.findall(
                r"[-+]?\d*\.\d+|\d+", eq12[1]
            )  # hedge constant fot the 2nd ticker
            # print("eq2_hedge: ", eq2_hedge)  # ['1.25']

            if len(eq2_hedge) > 0:
                eq2 = eq12[1].replace(eq2_hedge[0], "")
            else:
                eq2 = eq12[1]  # *NYSE:FTS

            eq2 = eq2.replace("*", "")

            # print("eq2: ", eq2)  # NYSE:FTS

            eq2_split = eq2.rsplit(":", maxsplit=1)
            eq2_ticker_almost = eq2_split[len(eq2_split) - 1]

            # print("eq2_split: ", eq2_split)  # ['NYSE', 'FTS']
            # print("eq2_ticker_almost: ", eq2_ticker_almost)  # FTS

            # check if the ticker security type is CASH or CRYPTO
            item = TickerModel.find_by_symbol(eq1_ticker_almost)

            if item:
                if item.sectype == "CASH":
                    fx1 = eq2_ticker_almost[0:3]  # get the first 3 char # USD
                    fx2 = eq2_ticker_almost[-3:]  # get the last 3 char # CAD
                    ticker_pair2 = fx1 + "." + fx2

                    # TODO: improve validity check
                    # check if valid fx pair
                    if len(ticker_pair2) != 7:  # check if it is in USD.CAD format
                        success_flag = False
                    # check for currency mismatch
                    if fx2 != item.currency:
                        currency_match = False
                        success_flag = False

                elif item.sectype == "CRYPTO":
                    cry2 = eq2_ticker_almost[-3:]  # get last 3 char
                    ticker_pair2 = eq2_ticker_almost.replace(".", "")
                    cry1 = eq2_ticker_almost[
                        0 : (len(ticker_pair2) - 3)
                    ]  # get the first 3 char
                    ticker_pair2 = cry1 + "." + cry2

                    # TODO: improve validity check
                    # check if valid cryptopair, accepts only USD pairs
                    if cry2 != item.currency or cry2 != "USD":
                        currency_match = False
                        success_flag = False

                else:

                    if (
                        "." in eq2_ticker_almost
                    ):  # For Class A,B type tickers EXP: BF.A BF.B
                        ticker_pair2 = eq2_ticker_almost.replace(
                            ".", " "
                        )  # convert Tradingview -> IB format
                    else:
                        ticker_pair2 = "".join(
                            char for char in eq2_ticker_almost if char.isalnum()
                        )

                        if eq2_ticker_almost != ticker_pair2:
                            success_flag = False

            # print("ticker_pair2: ", ticker_pair2)  # FTS

            if len(eq2_hedge) == 0:
                hedge_const = 1
            else:
                hedge_const = eq2_hedge[0]

            # print("hedge_const: ", hedge_const)  # False
            # print("problem_flag_final: ", success_flag)
            # print("ticker_type: ", self.ticker_type)

            self.ticker_type = "pair"
            self.ticker2 = ticker_pair2
            self.hedge_param = hedge_const

        if len(eq12) > 2:
            success_flag = False

        if not success_flag:
            self.order_status = "error"
            self.status_msg = "problematic ticker!"
            if not currency_match:
                self.status_msg = "currency mismatch!"

        return success_flag

    # to split stocks only
    def splitticker_stocks(self,) -> bool:

        # Split the received webhook equation into tickers and hedge parameters
        # Tested with Tradingview webhooks and Interactive Brokers ticker format
        # TESTED FOR THESE EQUATIONS:
        # pair_equation = "TEST 123"
        # pair_equation = "NYSE:LNT"
        # pair_equation = "0.7*NYSE:BF.A"
        # pair_equation = "NYSE:BF.A"
        # pair_equation = "NYSE:LNT-NYSE:FTS*2.2"
        # pair_equation = "NYSE:LNT*2-NYSE:FTS"
        # pair_equation = "NYSE:LNT-NYSE:FTS/3"
        # pair_equation = "1.3*NYSE:LNT-NYSE:FTS*2.2"
        # pair_equation = "NYSE:LNT-1.25*NYSE:FTS"
        # pair_equation = "LNT-1.25*NYSE:FTS"
        # pair_equation = "NYSE:LNT-NYSE:FTS"
        # pair_equation = "BF.A-0.7*NYSE:BF.B"

        success_flag = True

        eq12 = self.ticker.split("-")  # check if pair or single
        # print(eq12)  # ['LNT', '1.25*NYSE:FTS']

        if len(eq12) <= 2:

            eq1_hedge = re.findall(
                r"[-+]?\d*\.\d+|\d+", eq12[0]
            )  # hedge constant fot the 1st ticker
            # print("eq1_hedge: ", eq1_hedge)  # []

            if len(eq1_hedge) > 0:
                eq1 = eq12[0].replace(eq1_hedge[0], "")
            else:
                eq1 = eq12[0]  # LNT

            eq1 = eq1.replace("*", "")
            # print("eq1: ", eq1)  # LNT

            eq1_split = eq1.rsplit(":", maxsplit=1)
            eq1_ticker_almost = eq1_split[len(eq1_split) - 1]

            # print("eq1_split: ", eq1_split)  # ['LNT']
            # print("eq1_ticker_almost: ", eq1_ticker_almost)  # LNT

            if "." in eq1_ticker_almost:  # For Class A,B type tickers EXP: BF.A BF.B
                ticker_pair1 = eq1_ticker_almost.replace(
                    ".", " "
                )  # convert Tradingview -> IB format
            else:
                ticker_pair1 = "".join(
                    char for char in eq1_ticker_almost if char.isalnum()
                )

                if eq1_ticker_almost != ticker_pair1:
                    success_flag = False

            # print("ticker_pair1: ", ticker_pair1)  # LNT

            if len(eq1_hedge) != 0:
                if eq1_hedge[0] != 1:
                    success_flag = False

            # print("problem_flag_first: ", success_flag)

            self.ticker_type = "single"
            self.ticker1 = ticker_pair1

        if len(eq12) == 2:

            eq2_hedge = re.findall(
                r"[-+]?\d*\.\d+|\d+", eq12[1]
            )  # hedge constant fot the 2nd ticker
            # print("eq2_hedge: ", eq2_hedge)  # ['1.25']

            if len(eq2_hedge) > 0:
                eq2 = eq12[1].replace(eq2_hedge[0], "")
            else:
                eq2 = eq12[1]  # *NYSE:FTS

            eq2 = eq2.replace("*", "")

            # print("eq2: ", eq2)  # NYSE:FTS

            eq2_split = eq2.rsplit(":", maxsplit=1)
            eq2_ticker_almost = eq2_split[len(eq2_split) - 1]

            # print("eq2_split: ", eq2_split)  # ['NYSE', 'FTS']
            # print("eq2_ticker_almost: ", eq2_ticker_almost)  # FTS

            if "." in eq2_ticker_almost:  # For Class A,B type tickers EXP: BF.A BF.B
                ticker_pair2 = eq2_ticker_almost.replace(
                    ".", " "
                )  # convert Tradingview -> IB format
            else:
                ticker_pair2 = "".join(
                    char for char in eq2_ticker_almost if char.isalnum()
                )

                if eq2_ticker_almost != ticker_pair2:
                    success_flag = False

            # print("ticker_pair2: ", ticker_pair2)  # FTS

            if len(eq2_hedge) == 0:
                hedge_const = 1
            else:
                hedge_const = eq2_hedge[0]

            # print("hedge_const: ", hedge_const)  # False
            # print("problem_flag_final: ", success_flag)
            # print("ticker_type: ", self.ticker_type)

            self.ticker_type = "pair"
            self.ticker2 = ticker_pair2
            self.hedge_param = hedge_const

        if len(eq12) > 2:
            success_flag = False

        if not success_flag:
            self.order_status = "error"
            self.status_msg = "problematic ticker!"

        return success_flag

    # TODO: COMPLETE
    @classmethod
    def get_avg_slip(cls, ticker_name) -> List:
        pass

    @classmethod
    def find_by_orderid(cls, orderid) -> "SignalModel":

        return cls.query.filter(
            (cls.order_id1 == orderid) | (cls.order_id2 == orderid)
        ).first()
