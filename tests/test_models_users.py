"""
Test cases for user model
"""
import unittest
import os
from app import app
from db import db
from services.models.users import UserModel
from tests.factories import UserFactory

# rather than referring to an app directly, use a proxy,
# which points to the application handling the current activity
app.app_context().push()

DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///test.db")

######################################################################
#  TICKER MODEL TEST CASES
######################################################################


class TestUser(unittest.TestCase):
    """Test Cases for User Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        db.init_app(app)
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.drop_all()

    def setUp(self):
        """This runs before each test"""
        db.session.query(UserModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  TEST CASES
    ######################################################################

    def test_create_user(self):
        """It should create a User object and assert that it exists"""
        fake_user = UserFactory()

        user = UserModel(
            username=fake_user.username,
            password=fake_user.password,
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.username, fake_user.username)
        self.assertEqual(user.password, fake_user.password)

    def test_serialize_user(self):
        """It should return  a valid dictionary representation of the User with no visible password"""
        test_user = UserFactory()
        serial_test_user = test_user.json()

        self.assertEqual(serial_test_user["username"], test_user.username)
        with self.assertRaises(KeyError):
            serial_test_user["password"]

    def test_insert_user(self):
        """It should insert a User to the database and assert that it exists"""

        test_user = UserFactory()

        # get all rows
        users = UserModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(users.count(), 0)

        # insert user to the database
        test_user.insert()
        # read it back
        get_user = UserModel.find_by_username(test_user.username)

        # assert that id and username shows up in the database
        self.assertIsNotNone(get_user.rowid)
        self.assertEqual(test_user.username, get_user.username)

    def test_find_by_username(self):
        """It should find a User by its username"""

        test_user = UserFactory()

        # insert user to the database
        test_user.insert()
        # read it back
        get_user = UserModel.find_by_username(test_user.username)

        self.assertEqual(test_user.username, get_user.username)

    def test_update_user(self):
        """It should update a User in the database and assert that it is updated"""

        test_user = UserFactory()

        # insert user
        test_user.insert()

        new_username = "newuser"
        new_password = "newpassword"

        # get the user to update
        user_to_update = UserModel.find_by_username(test_user.username)

        user_to_update.username = new_username
        user_to_update.password = new_password

        # update with new information
        user_to_update.update()
        # fetch it back
        updated_user = UserModel.find_by_username(test_user.username)

        # assert that user is updated with new information
        self.assertEqual(updated_user.username, new_username)

    def test_get_users(self):
        """It should get number of defined User items from the database"""

        # create a batch of users and insert to the database
        for user in UserFactory.create_batch(5):
            user.insert()

        # get users from the database
        users = UserModel.get_rows("2")
        # assert that there are same number of records
        self.assertEqual(len(users), 2)

        # get users from the database
        users = UserModel.get_rows("3")
        # assert that there are same number of records
        self.assertEqual(len(users), 3)

        # get all users from the database
        users = UserModel.get_rows("0")
        # assert that there are same number of records
        self.assertEqual(users.count(), 5)

    def test_delete_user(self):
        """It should delete a User from the database"""

        test_user = UserFactory()

        # get all rows
        users = UserModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(users.count(), 0)

        # insert user to the database
        test_user.insert()
        # get all rows
        users = UserModel.get_rows("0")
        # assert that there are one record
        self.assertEqual(users.count(), 1)

        # delete user
        test_user.delete()
        # get all rows
        users = UserModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(users.count(), 0)
