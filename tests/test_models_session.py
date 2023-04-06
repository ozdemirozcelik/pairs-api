"""
Test cases for session model
"""
import unittest
import datetime
import pytz
import os
from app import app
from db import db
from services.models.session import SessionModel
from tests.factories import SessionFactory

# rather than referring to an app directly, use a proxy,
# which points to the application handling the current activity
app.app_context().push()

DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///test.db")

######################################################################
#  TICKER MODEL TEST CASES
######################################################################


class TestSession(unittest.TestCase):
    """Test Cases for Session Model"""

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
        db.session.query(SessionModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  TEST CASES
    ######################################################################

    def test_create_session(self):
        """It should create a Session object and assert that it exists"""
        fake_session = SessionFactory()

        session = SessionModel(
            value=fake_session.value,
            expiry=fake_session.expiry,
        )

        self.assertIsNotNone(session)
        self.assertEqual(session.value, fake_session.value)
        self.assertEqual(session.expiry, fake_session.expiry)

    def test_serialize_session(self):
        """It should return  a valid dictionary representation of the Session"""
        test_session = SessionFactory()
        serial_test_session = test_session.json()

        self.assertEqual(serial_test_session["value"], test_session.value)
        with self.assertRaises(KeyError):
            serial_test_session["expiry"]

    def test_insert_session(self):
        """It should insert a Session to the database and assert that it exists"""

        test_session = SessionFactory()

        # assert number of rows
        self.assertEqual(SessionModel.get_all().count(), 0)

        # insert session to the database
        test_session.insert()
        # read it back
        get_session = SessionModel.find_by_value(test_session.value)

        # assert that id and value shows up in the database
        self.assertIsNotNone(get_session.rowid)
        self.assertEqual(test_session.value, get_session.value)

    def test_find_session(self):
        """It should find a Session by its value"""

        test_session = SessionFactory()

        # insert session to the database
        test_session.insert()
        # read it back
        get_session = SessionModel.find_by_value(test_session.value)

        self.assertEqual(test_session.value, get_session.value)
        self.assertEqual(test_session.expiry, get_session.expiry)

    def test_delete_session(self):
        """It should delete a Session from the database"""

        test_session = SessionFactory()

        # assert number of rows
        self.assertEqual(SessionModel.get_all().count(), 0)

        # insert session to the database
        test_session.insert()
        # get all rows
        # assert number of rows
        self.assertEqual(SessionModel.get_all().count(), 1)

        # delete session
        test_session.delete()
        # get all rows
        # assert number of rows
        self.assertEqual(SessionModel.get_all().count(), 0)

    def test_get_all(self):
        """It should get all Sessions from the database"""

        # insert a batch of sessions
        for session in SessionFactory.create_batch(5):
            session.insert()

        self.assertEqual(SessionModel.get_all().count(), 5)

    def test_delete_all(self):
        """It should delete all Sessions from the database"""

        # insert a batch of sessions
        for session in SessionFactory.create_batch(5):
            session.insert()

        # assert number of rows
        self.assertEqual(SessionModel.get_all().count(), 5)

        # delete all sessions
        SessionModel.delete_all()
        self.assertEqual(SessionModel.get_all().count(), 0)

    def test_delete_expired(self):
        """It should delete all expired Sessions from the database"""

        # insert a batch of sessions
        for session in SessionFactory.create_batch(3):
            session.insert()

        # add a session with future expiry
        future_session = SessionFactory()
        future_session.expiry = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(
            days=1
        )
        future_session.insert()

        # assert number of rows
        self.assertEqual(SessionModel.get_all().count(), 4)

        # delete expired sessions & assert
        SessionModel.delete_expired()
        self.assertEqual(SessionModel.get_all().count(), 1)
