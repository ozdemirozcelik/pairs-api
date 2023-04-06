"""
Test cases for ticker model
"""
import unittest
import os
from app import app
from db import db
from services.models.tickers import TickerModel
from tests.factories import TickerFactory

# rather than referring to an app directly, use a proxy,
# which points to the application handling the current activity
app.app_context().push()

DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///test.db")

######################################################################
#  TICKER MODEL TEST CASES
######################################################################


class TestTicker(unittest.TestCase):
    """Test Cases for Ticker Model"""

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
        db.session.query(TickerModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  TEST CASES
    ######################################################################

    def test_create_ticker(self):
        """It should create a Ticker object and assert that it exists"""
        fake_ticker = TickerFactory()

        ticker = TickerModel(
            symbol=fake_ticker.symbol,
            sectype=fake_ticker.sectype,
            xch=fake_ticker.xch,
            prixch=fake_ticker.prixch,
            currency=fake_ticker.currency,
            active=fake_ticker.active,
            order_type=fake_ticker.order_type,
            active_pos=fake_ticker.active_pos,
            active_pnl=fake_ticker.active_pnl,
            active_cost=fake_ticker.active_cost,
        )

        self.assertIsNotNone(ticker)
        self.assertEqual(ticker.symbol, fake_ticker.symbol)
        self.assertEqual(ticker.sectype, fake_ticker.sectype)
        self.assertEqual(ticker.xch, fake_ticker.xch)
        self.assertEqual(ticker.prixch, fake_ticker.prixch)
        self.assertEqual(ticker.currency, fake_ticker.currency)
        self.assertEqual(ticker.active, fake_ticker.active)
        self.assertEqual(ticker.active_pos, fake_ticker.active_pos)
        self.assertEqual(ticker.active_pnl, fake_ticker.active_pnl)
        self.assertEqual(ticker.active_cost, fake_ticker.active_cost)

    def test_serialize_ticker(self):
        """It should return  a valid dictionary representation of the Ticker"""
        test_ticker = TickerFactory()
        serial_test_ticker = test_ticker.json()

        self.assertEqual(serial_test_ticker["symbol"], test_ticker.symbol)
        self.assertEqual(serial_test_ticker["sectype"], test_ticker.sectype)
        self.assertEqual(serial_test_ticker["xch"], test_ticker.xch)
        self.assertEqual(serial_test_ticker["prixch"], test_ticker.prixch)
        self.assertEqual(serial_test_ticker["currency"], test_ticker.currency)
        self.assertEqual(serial_test_ticker["active"], test_ticker.active)
        self.assertEqual(serial_test_ticker["active_pos"], test_ticker.active_pos)
        self.assertEqual(serial_test_ticker["active_pnl"], test_ticker.active_pnl)
        self.assertEqual(serial_test_ticker["active_cost"], test_ticker.active_cost)

    def test_insert_ticker(self):
        """It should insert a Ticker to the database and assert that it exists"""

        test_ticker = TickerFactory()

        # get all rows
        tickers = TickerModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(tickers.count(), 0)

        # insert ticker to the database
        test_ticker.insert()
        # read it back
        get_ticker = TickerModel.find_by_symbol(test_ticker.symbol)

        # assert that id and symbol shows up in the database
        self.assertIsNotNone(get_ticker.rowid)
        self.assertEqual(test_ticker.symbol, get_ticker.symbol)

    def test_find_ticker(self):
        """It should find a Ticker by its symbol"""

        test_ticker = TickerFactory()

        # insert ticker to the database
        test_ticker.insert()
        # read it back
        get_ticker = TickerModel.find_by_symbol(test_ticker.symbol)

        self.assertEqual(test_ticker.symbol, get_ticker.symbol)
        self.assertEqual(test_ticker.sectype, get_ticker.sectype)
        self.assertEqual(test_ticker.xch, get_ticker.xch)
        self.assertEqual(test_ticker.prixch, get_ticker.prixch)
        self.assertEqual(test_ticker.currency, get_ticker.currency)
        self.assertEqual(test_ticker.active, get_ticker.active)
        self.assertEqual(test_ticker.active_pos, get_ticker.active_pos)
        self.assertEqual(test_ticker.active_pnl, get_ticker.active_pnl)
        self.assertEqual(test_ticker.active_cost, get_ticker.active_cost)

    def test_update_ticker(self):
        """It should update a Ticker in the database and assert that it is updated"""

        test_ticker = TickerFactory()

        # insert ticker
        test_ticker.insert()

        new_sectype = "test"
        new_xch = "test"
        new_prixch = "test"
        new_currency = "test"
        new_order_type = "test"
        new_active = 10

        # get the ticker to update
        ticker_to_update = TickerModel.find_by_symbol(test_ticker.symbol)

        ticker_to_update.sectype = new_sectype
        ticker_to_update.xch = new_xch
        ticker_to_update.prixch = new_prixch
        ticker_to_update.currency = new_currency
        ticker_to_update.order_type = new_order_type
        ticker_to_update.active = new_active

        # update with new information
        ticker_to_update.update(False)
        # fetch it back
        updated_ticker = TickerModel.find_by_symbol(test_ticker.symbol)

        # assert that ticker is updated with new information
        self.assertEqual(updated_ticker.sectype, new_sectype)
        self.assertEqual(updated_ticker.xch, new_xch)
        self.assertEqual(updated_ticker.prixch, new_prixch)
        self.assertEqual(updated_ticker.currency, new_currency)
        self.assertEqual(updated_ticker.order_type, new_order_type)
        self.assertEqual(updated_ticker.active, new_active)

    def test_update_pnl(self):
        """It should update a Ticker PNL in the database and assert that it is updated"""

        test_ticker = TickerFactory()

        # insert ticker
        test_ticker.insert()

        new_active_pos = 111
        new_active_pnl = 222
        new_active_cost = 333

        # get the ticker to update
        ticker_to_update = TickerModel.find_by_symbol(test_ticker.symbol)

        ticker_to_update.active_pos = new_active_pos
        ticker_to_update.active_pnl = new_active_pnl
        ticker_to_update.active_cost = new_active_cost

        # update with new information
        ticker_to_update.update(True)
        # fetch it back
        updated_ticker = TickerModel.find_by_symbol(test_ticker.symbol)

        # assert that ticker is updated with new information
        self.assertEqual(updated_ticker.active_pos, new_active_pos)
        self.assertEqual(updated_ticker.active_pnl, new_active_pnl)
        self.assertEqual(updated_ticker.active_cost, new_active_cost)

    def test_get_tickers(self):
        """It should get number of defined Ticker items from the database"""

        # create a batch of tickers and insert to the database
        for ticker in TickerFactory.create_batch(5):
            ticker.insert()

        # get tickers from the database
        tickers = TickerModel.get_rows("2")
        # assert that there are same number of records
        self.assertEqual(len(tickers), 2)

        # get tickers from the database
        tickers = TickerModel.get_rows("3")
        # assert that there are same number of records
        self.assertEqual(len(tickers), 3)

        # get all tickers from the database
        tickers = TickerModel.get_rows("0")
        # assert that there are same number of records
        self.assertEqual(tickers.count(), 5)

    def test_delete_ticker(self):
        """It should delete a Ticker from the database"""

        test_ticker = TickerFactory()

        # get all rows
        tickers = TickerModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(tickers.count(), 0)

        # insert ticker to the database
        test_ticker.insert()
        # get all rows
        tickers = TickerModel.get_rows("0")
        # assert that there are one record
        self.assertEqual(tickers.count(), 1)

        # delete ticker
        test_ticker.delete()
        # get all rows
        tickers = TickerModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(tickers.count(), 0)

    def test_find_active_ticker(self):
        """It should get the first active ticker for given symbols"""

        # create a batch of tickers and insert to the database
        for ticker in TickerFactory.create_batch(4):
            ticker.insert()

        # get all tickers from the database
        selected_tickers = TickerModel.get_rows("0")

        # activate the first 2 tickers, and deactivate the remaining
        for i in range(2):
            selected_tickers[i].active = 1
            selected_tickers[3 - i].active = 0
            selected_tickers[i].update(False)

        # fetch and assert if returns an active ticker
        active_ticker = TickerModel.find_active_ticker(
            selected_tickers[0].symbol, selected_tickers[1].symbol
        )
        self.assertNotEqual(active_ticker, None)
        active_ticker = TickerModel.find_active_ticker(
            selected_tickers[2].symbol, selected_tickers[1].symbol
        )
        self.assertNotEqual(active_ticker, None)
        active_ticker = TickerModel.find_active_ticker(
            selected_tickers[2].symbol, selected_tickers[3].symbol
        )
        self.assertEqual(active_ticker, None)

    def test_get_active_tickers(self):
        """It should get the list of active tickers"""

        # create a batch of tickers and insert to the database
        for ticker in TickerFactory.create_batch(4):
            ticker.insert()

        # get three tickers from the database
        selected_tickers = TickerModel.get_rows("0")

        # activate the first 2 tickers, and deactivate the remaining
        for i in range(2):
            selected_tickers[i].active = 1
            selected_tickers[3 - i].active = 0
            selected_tickers[i].update(False)

        # assert if returns an active ticker
        active_tickers = TickerModel.get_active_tickers("0")
        self.assertEqual(active_tickers.count(), 2)
        active_tickers = TickerModel.get_active_tickers("1")
        self.assertEqual(len(active_tickers), 1)
        active_tickers = TickerModel.get_active_tickers("3")
        self.assertEqual(len(active_tickers), 2)

    def test_get_watchlist_tickers(self):
        """It should get the list of watchlist tickers"""

        # create a batch of tickers and insert to the database
        for ticker in TickerFactory.create_batch(4):
            ticker.insert()

        # get three tickers from the database
        selected_tickers = TickerModel.get_rows("0")

        # put the first 2 tickers to the watchlist, and activate the remaining
        for i in range(2):
            selected_tickers[i].active = -1
            selected_tickers[3 - i].active = 1
            selected_tickers[i].update(False)

        # assert if returns an active ticker
        watchlist_tickers = TickerModel.get_watchlist_tickers("0")
        self.assertEqual(watchlist_tickers.count(), 2)
        watchlist_tickers = TickerModel.get_watchlist_tickers("1")
        self.assertEqual(len(watchlist_tickers), 1)
        watchlist_tickers = TickerModel.get_watchlist_tickers("3")
        self.assertEqual(len(watchlist_tickers), 2)
