from db import db


class StockModel(db.Model):
    __tablename__ = 'stocks'

    rowid = db.Column(db.Integer, primary_key=True, autoincrement=True)  # using 'rowid' as the default key
    symbol = db.Column(db.String(40))  # sqlalchemy needs a primary key (either dummy or real)
    prixch = db.Column(db.String(40))
    secxch = db.Column(db.String(40))
    active = db.Column(db.Integer)

    def __init__(self, symbol, prixch, secxch, active):
        self.symbol = symbol
        self.prixch = prixch
        self.secxch = secxch
        self.active = active

    def json(self):
        return {'symbol': self.symbol, 'prixch': self.prixch, 'secxch': self.secxch, 'active': self.active}

    @classmethod
    def find_by_symbol(cls, symbol):

        return cls.query.filter_by(symbol=symbol).first()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # connection = sqlite3.connect('data.db', timeout=10)
        #
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "SELECT * FROM {table} WHERE symbol=?".format(table=TABLE_STOCKS)
        #     cursor.execute(query, (symbol,))
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

    def insert(self):

        db.session.add(self)
        db.session.commit()

    # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

    #     connection = sqlite3.connect('data.db', timeout=10)
    #
    #     try:
    #         cursor = connection.cursor()
    #
    #         query = "INSERT INTO {table} VALUES(?, ?, ?, ?)".format(table=TABLE_STOCKS)
    #
    #         cursor.execute(query, (self.symbol, self.prixch, self.secxch, self.active))
    #
    #         connection.commit()
    #
    #     except sqlite3.Error as e:  # handling the exception with generic SQL error code
    #         print('Database error occurred - ', e)  # better to log the error
    #         raise
    #
    #     finally:
    #         if connection:
    #             connection.close()  # disconnect the database even if exception occurs

    def update(self):

        item_to_update = self.query.filter_by(symbol=self.symbol).first()

        item_to_update.prixch = self.prixch
        item_to_update.secxch = self.secxch
        item_to_update.active = self.active

        db.session.commit()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # connection = sqlite3.connect('data.db', timeout=10)
        #
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "UPDATE {table} SET prixch=?, secxch=?, active=? WHERE symbol=?".format(table=TABLE_STOCKS)
        #
        #     cursor.execute(query, (self.prixch, self.secxch, self.active, self.symbol))
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
    def get_rows(cls, number_of_items):

        if number_of_items == "0":
            # return cls.query.order_by(desc("rowid")).all() # needs from sqlalchemy import desc
            return cls.query.order_by(cls.rowid.desc())  # better, no need to import
        else:
            return cls.query.order_by(cls.rowid.desc()).limit(number_of_items).all()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # if number_of_items == "0":
        #     query = "SELECT * FROM {table} ORDER BY rowid DESC".format(table=TABLE_STOCKS)
        # else:
        #     query = "SELECT * FROM {table} ORDER BY rowid DESC " \
        #             "LIMIT {number}".format(table=TABLE_STOCKS, number=number_of_items)
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

    def delete(self):

        db.session.delete(self)
        db.session.commit()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # connection = sqlite3.connect('data.db', timeout=10)
        #
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "DELETE FROM {table} WHERE symbol=?".format(table=TABLE_STOCKS)
        #     cursor.execute(query, (symbol,))
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
