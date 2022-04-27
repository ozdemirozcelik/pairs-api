import sqlite3

TABLE_USERS = 'users'


class UserModel:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def json(self):
        return {'username': self.username}

    @classmethod
    def find_by_username(cls, username):

        connection = sqlite3.connect('data.db', timeout=10)
        try:
            cursor = connection.cursor()

            query = "SELECT * FROM {table} WHERE username=?".format(table=TABLE_USERS)
            cursor.execute(query, (username,))
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

    # TODO: def find_by_id

    def insert(self):

        connection = sqlite3.connect('data.db', timeout=10)
        try:
            cursor = connection.cursor()

            query = "INSERT INTO {table} VALUES(?, ?)".format(table=TABLE_USERS)

            cursor.execute(query, (self.username, self.password))

            connection.commit()

        except sqlite3.Error as e:  # handling the exception with generic SQL error code
            print('Database error occurred - ', e)  # better to log the error
            raise

        finally:
            if connection:
                connection.close()  # disconnect the database even if exception occurs

    def update(self):

        connection = sqlite3.connect('data.db', timeout=10)
        try:
            cursor = connection.cursor()

            query = "UPDATE {table} SET password=? WHERE username=?".format(table=TABLE_USERS)

            cursor.execute(query, (self.password, self.username))

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
            query = "SELECT * FROM {table} ORDER BY rowid DESC".format(table=TABLE_USERS)
        else:
            query = "SELECT * FROM {table} ORDER BY rowid DESC " \
                    "LIMIT {number}".format(table=TABLE_USERS, number=number_of_items)

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
    def delete(username):

        connection = sqlite3.connect('data.db', timeout=10)
        try:
            cursor = connection.cursor()

            query = "DELETE FROM {table} WHERE username=?".format(table=TABLE_USERS)
            cursor.execute(query, (username,))

            connection.commit()

        except sqlite3.Error as e:
            print('Database error occurred - ', e)
            raise

        finally:
            if connection:
                connection.close()
