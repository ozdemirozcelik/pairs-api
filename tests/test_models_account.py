"""
Test cases for account model
"""
import unittest
import os
from app import app
from db import db
from models.account import AccountModel
from tests.factories import AccountFactory

# rather than referring to an app directly, use a proxy,
# which points to the application handling the current activity
app.app_context().push()

DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///test.db")

######################################################################
#  TICKER MODEL TEST CASES
######################################################################


class TestAccount(unittest.TestCase):
    """Test Cases for Account Model"""

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
        db.session.query(AccountModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()


    ######################################################################
    #  TEST CASES
    ######################################################################

    def test_create_account(self):
        """It should create an Account object and assert that it exists"""
        fake_account = AccountFactory()

        account = AccountModel(
            timestamp=fake_account.timestamp,
            AvailableFunds=fake_account.AvailableFunds,
            BuyingPower=fake_account.BuyingPower,
            DailyPnL=fake_account.DailyPnL,
            GrossPositionValue=fake_account.GrossPositionValue,
            MaintMarginReq=fake_account.MaintMarginReq,
            NetLiquidation=fake_account.NetLiquidation,
            RealizedPnL=fake_account.RealizedPnL,
            UnrealizedPnL=fake_account.UnrealizedPnL,
        )

        self.assertIsNotNone(account)
        self.assertEqual(account.timestamp, fake_account.timestamp)
        self.assertEqual(account.AvailableFunds, fake_account.AvailableFunds)
        self.assertEqual(account.BuyingPower, fake_account.BuyingPower)
        self.assertEqual(account.DailyPnL, fake_account.DailyPnL)
        self.assertEqual(account.GrossPositionValue, fake_account.GrossPositionValue)
        self.assertEqual(account.MaintMarginReq, fake_account.MaintMarginReq)
        self.assertEqual(account.NetLiquidation, fake_account.NetLiquidation)
        self.assertEqual(account.RealizedPnL, fake_account.RealizedPnL)
        self.assertEqual(account.UnrealizedPnL, fake_account.UnrealizedPnL)

    def test_serialize_account(self):
        """It should return a valid dictionary representation of the Account with no visible password"""
        test_account = AccountFactory()
        serial_test_account = test_account.json()

        self.assertEqual(
            serial_test_account["AvailableFunds"], test_account.AvailableFunds
        )
        self.assertEqual(serial_test_account["BuyingPower"], test_account.BuyingPower)
        self.assertEqual(serial_test_account["DailyPnL"], test_account.DailyPnL)
        self.assertEqual(
            serial_test_account["GrossPositionValue"], test_account.GrossPositionValue
        )
        self.assertEqual(
            serial_test_account["MaintMarginReq"], test_account.MaintMarginReq
        )
        self.assertEqual(
            serial_test_account["NetLiquidation"], test_account.NetLiquidation
        )
        self.assertEqual(serial_test_account["RealizedPnL"], test_account.RealizedPnL)
        self.assertEqual(
            serial_test_account["UnrealizedPnL"], test_account.UnrealizedPnL
        )

    def test_insert_account(self):
        """It should insert an Account to the database and assert that it exists"""

        test_account = AccountFactory()

        # get all rows
        account = AccountModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(account.count(), 0)

        # insert account to the database
        test_account.insert()
        # get rowid
        account = AccountModel.get_rows("0")
        rowid = account.all()[0].rowid
        self.assertEqual(account.count(), 1)      
        # read it back
        get_account = AccountModel.find_by_rowid(rowid)

        # assert that id and accountname shows up in the database
        self.assertIsNotNone(get_account.rowid)
        self.assertEqual(test_account.AvailableFunds, get_account.AvailableFunds)

    def test_find_by_rowid(self):
        """It should find an Account by its rowid"""

        test_account = AccountFactory()

        # insert account to the database
        test_account.insert()
        # get rowid
        account = AccountModel.get_rows("0")
        rowid = account.all()[0].rowid
        self.assertEqual(account.count(), 1)     
        # read it back
        get_account = AccountModel.find_by_rowid(rowid)

        self.assertEqual(test_account.rowid, get_account.rowid)

    def test_update_account(self):
        """It should update a Account in the database and assert that it is updated"""

        test_account = AccountFactory()

        # insert account
        test_account.insert()

        new_BuyingPower = 10000
        new_DailyPnL = -100
        
        # get rowid
        account = AccountModel.get_rows("0")
        rowid = account.all()[0].rowid
        self.assertEqual(account.count(), 1)   

        # get the account to update
        account_to_update = AccountModel.find_by_rowid(rowid)

        account_to_update.BuyingPower = new_BuyingPower
        account_to_update.DailyPnL = new_DailyPnL

        # update with new information
        account_to_update.update(rowid)
        # fetch it back
        updated_account = AccountModel.find_by_rowid(rowid)

        # assert that account is updated with new information
        self.assertEqual(updated_account.BuyingPower, new_BuyingPower)
        self.assertEqual(updated_account.DailyPnL, new_DailyPnL)

    def test_get_account(self):
        """It should get number of defined Account items from the database"""

        # create a batch of account and insert to the database
        for account in AccountFactory.create_batch(5):
            account.insert()

        # get account from the database
        account = AccountModel.get_rows("2")
        # assert that there are same number of records
        self.assertEqual(account.count(), 2)

        # get account from the database
        account = AccountModel.get_rows("3")
        # assert that there are same number of records
        self.assertEqual(account.count(), 3)

        # get all account from the database
        account = AccountModel.get_rows("0")
        # assert that there are same number of records
        self.assertEqual(account.count(), 5)

    def test_delete_account(self):
        """It should delete a Account from the database"""

        test_account = AccountFactory()

        # get all rows
        account = AccountModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(account.count(), 0)

        # insert account to the database
        test_account.insert()
        # get all rows
        account = AccountModel.get_rows("0")
        # assert that there are one record
        self.assertEqual(account.count(), 1)

        # delete account
        test_account.delete()
        # get all rows
        account = AccountModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(account.count(), 0)
