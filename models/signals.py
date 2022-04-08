import sqlite3

TABLE_SIGNALS = 'signals'
PASSPHRASE = 'webhook'


class SignalModel:

    def __init__(self, rowid, timestamp, ticker, order_action, order_contracts, order_price, mar_pos, mar_pos_size,
                 pre_mar_pos, pre_mar_pos_size, order_comment, order_status):
        self.rowid = rowid
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

    def json(self):
        return {'rowid': self.rowid, 'timestamp': self.timestamp, 'ticker': self.ticker,
                'order_action': self.order_action, 'order_contracts': self.order_contracts,
                'order_price': self.order_price, 'mar_pos': self.mar_pos, 'mar_pos_size': self.mar_pos_size,
                'pre_mar_pos': self.pre_mar_pos, 'pre_mar_pos_size': self.pre_mar_pos_size,
                'order_comment': self.order_comment, 'order_status': self.order_status}

    @staticmethod
    def passphrase_wrong(passphrase):
        if passphrase == PASSPHRASE:
            return False
        return True

    @classmethod
    def find_by_rowid(cls, rowid):

        if rowid == 0:
            return None

        connection = sqlite3.connect('data.db', timeout=10)

        try:
            cursor = connection.cursor()

            query = "SELECT rowid, * FROM {table} WHERE rowid=?".format(table=TABLE_SIGNALS)
            cursor.execute(query, (rowid,))
            row = cursor.fetchone()

        except sqlite3.Error as e:
            print('Database error occurred - ', e)
            raise

        finally:
            if connection:
                connection.close()

        if row:
            return cls(*row)

        return None

    def insert(self):

        connection = sqlite3.connect('data.db', timeout=10)

        try:
            cursor = connection.cursor()

            query = "INSERT INTO {table} (ticker, order_action, order_contracts, order_price," \
                    "mar_pos, mar_pos_size, pre_mar_pos, pre_mar_pos_size, order_comment, order_status) " \
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(table=TABLE_SIGNALS)

            cursor.execute(query, (self.ticker, self.order_action, self.order_contracts, self.order_price,
                                   self.mar_pos, self.mar_pos_size, self.pre_mar_pos, self.pre_mar_pos_size,
                                   self.order_comment, self.order_status))

            connection.commit()

        except sqlite3.Error as e:  # handling the exception with generic SQL error code
            print('Database error occurred - ', e)  # better to log the error
            raise

        finally:
            if connection:
                connection.close()  # disconnect the database even if exception occurs

    def update(self, rowid):

        connection = sqlite3.connect('data.db')

        try:
            cursor = connection.cursor()

            query = "UPDATE {table} SET ticker=?, order_action=?, order_contracts=?,order_price=?," \
                    "mar_pos=?, mar_pos_size=?, pre_mar_pos=?, pre_mar_pos_size=?, order_comment=?, order_status=? " \
                    "WHERE rowid=?".format(table=TABLE_SIGNALS)

            cursor.execute(query, (self.ticker, self.order_action, self.order_contracts, self.order_price,
                                   self.mar_pos, self.mar_pos_size, self.pre_mar_pos, self.pre_mar_pos_size,
                                   self.order_comment, self.order_status, rowid))

            connection.commit()

        except sqlite3.Error as e:
            print('Database error occurred - ', e)
            raise

        finally:
            if connection:
                connection.close()

    @classmethod
    def get_rows(cls, number_of_items):

        if number_of_items == "0":
            query = "SELECT rowid, * FROM {table} ORDER BY rowid DESC".format(table=TABLE_SIGNALS)
        else:
            query = "SELECT rowid, * FROM {table} ORDER BY rowid DESC " \
                    "LIMIT {number}".format(table=TABLE_SIGNALS, number=number_of_items)

        connection = sqlite3.connect('data.db', timeout=10)

        try:
            cursor = connection.cursor()

            cursor.execute(query)

            result = cursor.fetchall()  # Keep the result in memory after closing the database

        except sqlite3.Error as e:
            print('Database error occurred - ', e)
            raise

        finally:
            if connection:
                connection.close()

        items = []

        for row in result:
            items.append(cls(*row))

        return items

    @staticmethod
    def delete_name(rowid):

        connection = sqlite3.connect('data.db', timeout=10)

        try:
            cursor = connection.cursor()

            query = "DELETE FROM {table} WHERE rowid=?".format(table=TABLE_SIGNALS)
            cursor.execute(query, (rowid,))

            connection.commit()

        except sqlite3.Error as e:
            print('Database error occurred - ', e)
            raise

        finally:
            if connection:
                connection.close()
