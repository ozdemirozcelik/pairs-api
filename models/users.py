from typing import Dict, List  # for type hinting
from db import db

UserJSON = Dict[str, str]  # custom type hint


class UserModel(db.Model):
    __tablename__ = "users"

    # sqlalchemy needs a primary key (either dummy or real)
    rowid = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )  # using 'rowid' as the default key
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def json(self) -> UserJSON:
        return {"username": self.username}

    @classmethod
    def find_by_username(cls, username) -> "UserModel":

        return cls.query.filter_by(username=username).first()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:

        # connection = sqlite3.connect('data.db', timeout=10)
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "SELECT * FROM {table} WHERE username=?".format(table=TABLE_USERS)
        #     cursor.execute(query, (username,))
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
        #     query = "INSERT INTO {table} VALUES(?, ?)".format(table=TABLE_USERS)
        #
        #     cursor.execute(query, (self.username, self.password))
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

        item_to_update = self.query.filter_by(username=self.username).first()

        item_to_update.password = self.password

        db.session.commit()

        # # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:
        #
        # connection = sqlite3.connect('data.db', timeout=10)
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "UPDATE {table} SET password=? WHERE username=?".format(table=TABLE_USERS)
        #
        #     cursor.execute(query, (self.password, self.username))
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
        #     query = "SELECT * FROM {table} ORDER BY rowid DESC".format(table=TABLE_USERS)
        # else:
        #     query = "SELECT * FROM {table} ORDER BY rowid DESC " \
        #             "LIMIT {number}".format(table=TABLE_USERS, number=number_of_items)
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

    @staticmethod
    def delete(username) -> None:

        db.session.delete(username)
        db.session.commit()

        # KEEPING THE SQL CODE THAT FUNCTIONS THE SAME FOR COMPARISON PURPOSES:
        #
        # connection = sqlite3.connect('data.db', timeout=10)
        # try:
        #     cursor = connection.cursor()
        #
        #     query = "DELETE FROM {table} WHERE username=?".format(table=TABLE_USERS)
        #     cursor.execute(query, (username,))
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
