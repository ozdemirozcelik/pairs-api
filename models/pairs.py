import sqlite3

TABLE_PAIRS = 'pairs'


class PairModel:

    def __init__(self, name, hedge, status):
        self.name = name
        self.hedge = hedge
        self.status = status

    def json(self):
        return {'name': self.name, 'hedge': self.hedge, 'status': self.status}

    @classmethod
    def find_by_name(cls, name):

        try:
            connection = sqlite3.connect('data.db', timeout=10)
            cursor = connection.cursor()

            query = "SELECT * FROM {table} WHERE name=?".format(table=TABLE_PAIRS)
            cursor.execute(query, (name,))
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

        try:
            connection = sqlite3.connect('data.db', timeout=10)

            cursor = connection.cursor()

            query = "INSERT INTO {table} VALUES(?, ?, ?)".format(table=TABLE_PAIRS)

            cursor.execute(query, (self.name, self.hedge, self.status))

            connection.commit()

        except sqlite3.Error as e:  # handling the exception with generic SQL error code
            print('Database error occurred - ', e)  # better to log the error
            raise

        finally:
            if connection:
                connection.close()  # disconnect the database even if exception occurs


    def update(self):

        try:
            connection = sqlite3.connect('data.db')

            cursor = connection.cursor()

            query = "UPDATE {table} SET hedge=?, status=? WHERE name=?".format(table=TABLE_PAIRS)

            cursor.execute(query, (self.hedge, self.status, self.name))

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
            query = "SELECT * FROM {table} ORDER BY rowid DESC".format(table=TABLE_PAIRS)
        else:
            query = "SELECT * FROM {table} ORDER BY rowid DESC " \
                    "LIMIT {number}".format(table=TABLE_PAIRS, number=number_of_items)

        try:
            connection = sqlite3.connect('data.db', timeout=10)

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

    # @jwt_required()
    @staticmethod
    def delete_name(name):

        try:
            connection = sqlite3.connect('data.db', timeout=10)
            cursor = connection.cursor()

            query = "DELETE FROM {table} WHERE name=?".format(table=TABLE_PAIRS)
            cursor.execute(query, (name,))

            connection.commit()

        except sqlite3.Error as e:
            print('Database error occurred - ', e)
            raise

        finally:
            if connection:
                connection.close()
