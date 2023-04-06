"""
Test cases for pair model
"""
import unittest
import os
from app import app
from db import db
from services.models.pairs import PairModel
from tests.factories import PairFactory

# rather than referring to an app directly, use a proxy,
# which points to the application handling the current activity
app.app_context().push()

DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///test.db")

######################################################################
#  PAIR MODEL TEST CASES
######################################################################


class TestPair(unittest.TestCase):
    """Test Cases for Pair Model"""

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
        db.session.query(PairModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  TEST CASES
    ######################################################################

    def test_create_pair(self):
        """It should create a Pair object and assert that it exists"""
        fake_pair = PairFactory()

        pair = PairModel(
            name=fake_pair.name,
            hedge=fake_pair.hedge,
            status=fake_pair.status,
            ticker1=fake_pair.ticker1,
            ticker2=fake_pair.ticker2,
            notes=fake_pair.notes,
            contracts=fake_pair.contracts,
            act_price=fake_pair.act_price,
            sma=fake_pair.sma,
            sma_dist=fake_pair.sma_dist,
            std=fake_pair.std,
        )

        self.assertIsNotNone(pair)
        self.assertEqual(pair.name, fake_pair.name)
        self.assertEqual(pair.hedge, fake_pair.hedge)
        self.assertEqual(pair.status, fake_pair.status)
        self.assertEqual(pair.ticker1, fake_pair.ticker1)
        self.assertEqual(pair.ticker2, fake_pair.ticker2)
        self.assertEqual(pair.notes, fake_pair.notes)
        self.assertEqual(pair.contracts, fake_pair.contracts)
        self.assertEqual(pair.act_price, fake_pair.act_price)
        self.assertEqual(pair.sma, fake_pair.sma)
        self.assertEqual(pair.sma_dist, fake_pair.sma_dist)
        self.assertEqual(pair.std, fake_pair.std)

    def test_serialize_pair(self):
        """It should return  a valid dictionary representation of the Pair"""
        test_pair = PairFactory()
        serial_test_pair = test_pair.json()

        self.assertEqual(serial_test_pair["name"], test_pair.name)
        self.assertEqual(serial_test_pair["hedge"], test_pair.hedge)
        self.assertEqual(serial_test_pair["status"], test_pair.status)
        self.assertEqual(serial_test_pair["ticker1"], test_pair.ticker1)
        self.assertEqual(serial_test_pair["ticker2"], test_pair.ticker2)
        self.assertEqual(serial_test_pair["notes"], test_pair.notes)
        self.assertEqual(serial_test_pair["contracts"], test_pair.contracts)
        self.assertEqual(serial_test_pair["act_price"], test_pair.act_price)
        self.assertEqual(serial_test_pair["sma"], test_pair.sma)
        self.assertEqual(serial_test_pair["sma_dist"], test_pair.sma_dist)
        self.assertEqual(serial_test_pair["std"], test_pair.std)

    def test_insert_pair(self):
        """It should insert a Pair to the database and assert that it exists"""

        test_pair = PairFactory()

        # get all rows
        pairs = PairModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(pairs.count(), 0)

        # insert pair to the database
        test_pair.insert()
        # read it back
        get_pair = PairModel.find_by_name(test_pair.name)

        # assert that id and name shows up in the database
        self.assertIsNotNone(get_pair.rowid)
        self.assertEqual(test_pair.name, get_pair.name)

    def test_find_pair(self):
        """It should find a Pair by its name"""

        test_pair = PairFactory()

        # insert pair to the database
        test_pair.insert()
        # read it back
        get_pair = PairModel.find_by_name(test_pair.name)

        self.assertEqual(test_pair.name, get_pair.name)
        self.assertEqual(test_pair.hedge, get_pair.hedge)
        self.assertEqual(test_pair.status, get_pair.status)
        self.assertEqual(test_pair.ticker1, get_pair.ticker1)
        self.assertEqual(test_pair.ticker2, get_pair.ticker2)
        self.assertEqual(test_pair.notes, get_pair.notes)
        self.assertEqual(test_pair.contracts, get_pair.contracts)
        self.assertEqual(test_pair.act_price, get_pair.act_price)
        self.assertEqual(test_pair.sma, get_pair.sma)
        self.assertEqual(test_pair.sma_dist, get_pair.sma_dist)
        self.assertEqual(test_pair.std, get_pair.std)

    def test_update_pair(self):
        """It should update a Pair in the database and assert that it is updated"""

        test_pair = PairFactory()

        # insert pair
        test_pair.insert()

        new_name = "TEST-PAIR"
        new_hedge = 1.5
        new_ticker1 = "TEST"
        new_ticker2 = "PAIR"
        new_status = 0
        new_contracts = 100

        # get the pair to update
        pair_to_update = PairModel.find_by_name(test_pair.name)

        pair_to_update.name = new_name
        pair_to_update.hedge = new_hedge
        pair_to_update.ticker1 = new_ticker1
        pair_to_update.ticker2 = new_ticker2
        pair_to_update.status = new_status
        pair_to_update.contracts = new_contracts

        # update with new information
        pair_to_update.update()
        # fetch it back
        updated_pair = PairModel.find_by_name(test_pair.name)

        # assert that pair is updated with new information
        self.assertEqual(updated_pair.name, new_name)
        self.assertEqual(updated_pair.hedge, new_hedge)
        self.assertEqual(updated_pair.ticker1, new_ticker1)
        self.assertEqual(updated_pair.ticker2, new_ticker2)
        self.assertEqual(updated_pair.status, new_status)
        self.assertEqual(updated_pair.contracts, new_contracts)

    def test_get_pairs(self):
        """It should get number of defined Pair items from the database"""

        # create a batch of pairs and insert to the database
        for pair in PairFactory.create_batch(5):
            pair.insert()

        # get pairs from the database
        pairs = PairModel.get_rows("2")
        # assert that there are same number of records
        self.assertEqual(len(pairs), 2)

        # get pairs from the database
        pairs = PairModel.get_rows("3")
        # assert that there are same number of records
        self.assertEqual(len(pairs), 3)

        # get all pairs from the database
        pairs = PairModel.get_rows("0")
        # assert that there are same number of records
        self.assertEqual(pairs.count(), 5)

    def test_delete_pair(self):
        """It should delete a Pair from the database"""

        test_pair = PairFactory()

        # get all rows
        pairs = PairModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(pairs.count(), 0)

        # insert pair to the database
        test_pair.insert()
        # get all rows
        pairs = PairModel.get_rows("0")
        # assert that there are one record
        self.assertEqual(pairs.count(), 1)

        # delete pair
        test_pair.delete()
        # get all rows
        pairs = PairModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(pairs.count(), 0)

    def test_get_active_pairs(self):
        """It should get the list of active pairs"""

        # create a batch of pairs and insert to the database
        for pair in PairFactory.create_batch(4):
            pair.insert()

        # get three pairs from the database
        selected_pairs = PairModel.get_rows("0")

        # activate the first 2 pairs, and deactivate the remaining
        for i in range(2):
            selected_pairs[i].status = 1
            selected_pairs[3 - i].status = 0
            selected_pairs[i].update()

        # assert if returns an active pair
        active_pairs = PairModel.get_active_pairs("0")
        self.assertEqual(active_pairs.count(), 2)
        active_pairs = PairModel.get_active_pairs("1")
        self.assertEqual(len(active_pairs), 1)
        active_pairs = PairModel.get_active_pairs("3")
        self.assertEqual(len(active_pairs), 2)

    def test_get_watchlist_pairs(self):
        """It should get the list of watchlist pairs"""

        # create a batch of pairs and insert to the database
        for pair in PairFactory.create_batch(4):
            pair.insert()

        # get three pairs from the database
        selected_pairs = PairModel.get_rows("0")

        # put the first 2 pairs to the watchlist, and activate the remaining
        for i in range(2):
            selected_pairs[i].status = -1
            selected_pairs[3 - i].status = 1
            selected_pairs[i].update()

        # assert if returns an active pair
        watchlist_pairs = PairModel.get_watchlist_pairs("0")
        self.assertEqual(watchlist_pairs.count(), 2)
        watchlist_pairs = PairModel.get_watchlist_pairs("1")
        self.assertEqual(len(watchlist_pairs), 1)
        watchlist_pairs = PairModel.get_watchlist_pairs("3")
        self.assertEqual(len(watchlist_pairs), 2)

    def test_combine_tickers(self):
        """It should get ticker1 and ticker2 and create a pair name"""

        test_pair = PairFactory()
        test_pair.ticker1 = "TE-ST"
        test_pair.insert()

        self.assertFalse(test_pair.combineticker())
        self.assertTrue(test_pair.notes, "problematic ticker!")

        test_pair = PairFactory()
        ticker1 = test_pair.ticker1
        ticker2 = test_pair.ticker2

        if test_pair.combineticker():
            self.assertTrue(test_pair.name, ticker1 + "-" + ticker2)

    def test_find_active_ticker(self):
        """It should return an active pair if ticker is already active in that pair"""

        ticker1_names = []

        # create a batch of pairs and insert to the database
        for pair in PairFactory.create_batch(4):
            ticker1_names.append(pair.ticker1)
            pair.insert()

        # get all pairs from the database (ascending order)
        selected_pairs = PairModel.get_rows("0")

        # activate the most recent 2 pairs and get ticker1 names
        for i in range(3, 1, -1):
            selected_pairs[i].status = 1
            selected_pairs[i].update()

        # assert the list values
        self.assertEqual(selected_pairs[3].ticker1, ticker1_names[0])
        self.assertEqual(selected_pairs[2].ticker1, ticker1_names[1])
        self.assertEqual(selected_pairs[1].ticker1, ticker1_names[2])

        # find and assert
        pair_found = PairModel.find_active_ticker(ticker1_names[0])
        self.assertEqual(pair_found.ticker1, ticker1_names[0])
        pair_found = PairModel.find_active_ticker(ticker1_names[1])
        self.assertEqual(pair_found.ticker1, ticker1_names[1])
        pair_found = PairModel.find_active_ticker(ticker1_names[2])
        self.assertIsNone(pair_found)
