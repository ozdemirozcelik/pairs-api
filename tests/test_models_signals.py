"""
Test cases for signal model
"""
import unittest
import os
from app import app
from db import db
from models.signals import SignalModel
from models.pairs import PairModel
from models.tickers import TickerModel
from tests.factories import SignalFactory
from tests.factories import PairFactory
from tests.factories import TickerFactory
from app import configs
import datetime

# rather than referring to an app directly, use a proxy,
# which points to the application handling the current activity
app.app_context().push()

DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///test.db")

######################################################################
#  SIGNAL MODEL TEST CASES
######################################################################


class TestSignal(unittest.TestCase):
    """Test Cases for Signal Model"""

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
        db.session.query(SignalModel).delete()  # clean up the last tests
        db.session.query(PairModel).delete()  # clean up the last tests
        db.session.query(TickerModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  TEST CASES
    ######################################################################

    def test_create_signal(self):
        """It should create a signal object and assert that it exists"""
        fake_signal = SignalFactory()

        signal = SignalModel(
            timestamp=fake_signal.timestamp,
            ticker=fake_signal.ticker,
            order_action=fake_signal.order_action,
            order_contracts=fake_signal.order_contracts,
            order_price=fake_signal.order_price,
            mar_pos=fake_signal.mar_pos,
            mar_pos_size=fake_signal.mar_pos_size,
            pre_mar_pos=fake_signal.pre_mar_pos,
            pre_mar_pos_size=fake_signal.pre_mar_pos_size,
            order_comment=fake_signal.order_comment,
            order_status=fake_signal.order_status,
            ticker_type=fake_signal.ticker_type,
            ticker1=fake_signal.ticker1,
            ticker2=fake_signal.ticker2,
            hedge_param=fake_signal.hedge_param,
            order_id1=fake_signal.order_id1,
            order_id2=fake_signal.order_id2,
            price1=fake_signal.price1,
            price2=fake_signal.price2,
            fill_price=fake_signal.fill_price,
            slip=fake_signal.slip,
            error_msg=fake_signal.error_msg,
            status_msg=fake_signal.status_msg,
        )

        self.assertIsNotNone(signal)
        self.assertEqual(signal.timestamp, fake_signal.timestamp)
        self.assertEqual(signal.ticker, fake_signal.ticker)
        self.assertEqual(signal.order_action, fake_signal.order_action)
        self.assertEqual(signal.order_contracts, fake_signal.order_contracts)
        self.assertEqual(signal.order_price, fake_signal.order_price)
        self.assertEqual(signal.mar_pos, fake_signal.mar_pos)
        self.assertEqual(signal.mar_pos_size, fake_signal.mar_pos_size)
        self.assertEqual(signal.pre_mar_pos, fake_signal.pre_mar_pos)
        self.assertEqual(signal.order_comment, fake_signal.order_comment)
        self.assertEqual(signal.order_status, fake_signal.order_status)
        self.assertEqual(signal.ticker_type, fake_signal.ticker_type)
        self.assertEqual(signal.ticker1, fake_signal.ticker1)
        self.assertEqual(signal.ticker2, fake_signal.ticker2)
        self.assertEqual(signal.hedge_param, fake_signal.hedge_param)
        self.assertEqual(signal.order_id1, fake_signal.order_id1)
        self.assertEqual(signal.order_id2, fake_signal.order_id2)
        self.assertEqual(signal.price1, fake_signal.price1)
        self.assertEqual(signal.price2, fake_signal.price2)
        self.assertEqual(signal.fill_price, fake_signal.fill_price)
        self.assertEqual(signal.slip, fake_signal.slip)
        self.assertEqual(signal.error_msg, fake_signal.error_msg)
        self.assertEqual(signal.status_msg, fake_signal.status_msg)

    def test_serialize_signal(self):
        """It should return  a valid dictionary representation of the Signal"""
        test_signal = SignalFactory()
        serial_test_signal = test_signal.json()

        self.assertEqual(serial_test_signal["timestamp"], str(test_signal.timestamp))
        self.assertEqual(serial_test_signal["ticker"], test_signal.ticker)
        self.assertEqual(serial_test_signal["order_action"], test_signal.order_action)
        self.assertEqual(
            serial_test_signal["order_contracts"], test_signal.order_contracts
        )
        self.assertEqual(serial_test_signal["order_price"], test_signal.order_price)
        self.assertEqual(serial_test_signal["mar_pos"], test_signal.mar_pos)
        self.assertEqual(serial_test_signal["mar_pos_size"], test_signal.mar_pos_size)
        self.assertEqual(serial_test_signal["pre_mar_pos"], test_signal.pre_mar_pos)
        self.assertEqual(serial_test_signal["order_comment"], test_signal.order_comment)
        self.assertEqual(serial_test_signal["order_status"], test_signal.order_status)
        self.assertEqual(serial_test_signal["ticker_type"], test_signal.ticker_type)
        self.assertEqual(serial_test_signal["ticker1"], test_signal.ticker1)
        self.assertEqual(serial_test_signal["ticker2"], test_signal.ticker2)
        self.assertEqual(serial_test_signal["hedge_param"], test_signal.hedge_param)
        self.assertEqual(serial_test_signal["order_id1"], test_signal.order_id1)
        self.assertEqual(serial_test_signal["order_id2"], test_signal.order_id2)
        self.assertEqual(serial_test_signal["price1"], test_signal.price1)
        self.assertEqual(serial_test_signal["price2"], test_signal.price2)
        self.assertEqual(serial_test_signal["fill_price"], test_signal.fill_price)
        self.assertEqual(serial_test_signal["slip"], test_signal.slip)
        self.assertEqual(serial_test_signal["error_msg"], test_signal.error_msg)
        self.assertEqual(serial_test_signal["status_msg"], test_signal.status_msg)

    def test_passphrase_wrong(self):
        """It should return  True if passphrase is wrong"""

        phrase = "wrong"
        self.assertTrue(SignalModel.passphrase_wrong(phrase))

        default_phrase = configs.get("SECRET", "WEBHOOK_PASSPHRASE")
        self.assertFalse(SignalModel.passphrase_wrong(default_phrase))

    def test_insert_signal(self):
        """It should insert a Signal to the database and assert that it exists"""

        test_signal = SignalFactory()

        # get all rows
        signals = SignalModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(signals.count(), 0)

        # insert one signal to the database
        test_signal.insert()
        # get rowid
        signals = SignalModel.get_rows("0")
        rowid = signals.all()[0].rowid
        self.assertEqual(signals.count(), 1)     
        # read it back
        get_signal = SignalModel.find_by_rowid(rowid)

        # assert that id and name shows up in the database
        self.assertIsNotNone(get_signal.rowid)
        self.assertEqual(test_signal.ticker, get_signal.ticker)

    def test_find_signal(self):
        """It should find a Signal by its rowid and assert the ticker name"""

        tickers = []

        # insert a batch of signals to the database
        for signal in SignalFactory.create_batch(4):
            signal.insert()
            tickers.append(signal.ticker)

        # get the first rowid
        signals = SignalModel.get_rows("0")
        rowid = signals.all()[0].rowid-3

        # read the first signal
        first_signal = SignalModel.find_by_rowid(rowid)

        # read the last signal
        last_signal = SignalModel.find_by_rowid(rowid+3)

        self.assertEqual(tickers[0], first_signal.ticker)
        self.assertEqual(tickers[3], last_signal.ticker)

    def test_update_signal(self):
        """It should update a Signal by its rowid in the database and assert that it is updated"""

        test_signal = SignalFactory()

        # insert signal
        test_signal.insert()

        order_action = "BUY"
        order_price = 50.1
        order_comment = "TEST COMMENT"
        
        # get rowid
        signals = SignalModel.get_rows("0")
        rowid = signals.all()[0].rowid
        self.assertEqual(signals.count(), 1)  

        # get the signal to update
        signal_to_update = SignalModel.find_by_rowid(rowid)

        signal_to_update.order_action = order_action
        signal_to_update.order_price = order_price
        signal_to_update.order_comment = order_comment

        # update with new information
        signal_to_update.update(rowid)
        # fetch it back
        updated_signal = SignalModel.find_by_rowid(rowid)

        # assert that signal is updated with new information
        self.assertEqual(updated_signal.order_action, order_action)
        self.assertEqual(updated_signal.order_price, order_price)
        self.assertEqual(updated_signal.order_comment, order_comment)

    def test_get_signals(self):
        """It should get number of defined Signal items from the database"""

        # create a batch of signals and insert to the database
        for signal in SignalFactory.create_batch(5):
            signal.insert()

        # get signals from the database
        signals = SignalModel.get_rows("2")
        # assert that there are same number of records
        self.assertEqual(signals.count(), 2)

        # get signals from the database
        signals = SignalModel.get_rows("3")
        # assert that there are same number of records
        self.assertEqual(signals.count(), 3)

        # get all signals from the database
        signals = SignalModel.get_rows("0")
        # assert that there are same number of records
        self.assertEqual(signals.count(), 5)

    def test_delete_signal(self):
        """It should delete a Signal from the database"""

        test_signal = SignalFactory()

        # get all rows
        signals = SignalModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(signals.count(), 0)

        # insert signal to the database
        test_signal.insert()
        # get all rows
        signals = SignalModel.get_rows("0")
        # assert that there are one record
        self.assertEqual(signals.count(), 1)

        # delete signal
        test_signal.delete()
        # get all rows
        signals = SignalModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(signals.count(), 0)

    def test_get_list_ticker(self):
        """It should get a list of Signals for a given ticker name (pair or single)"""

        test_signal = SignalFactory()

        # get all rows
        signals = SignalModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(signals.count(), 0)

        # insert one signal to the database
        test_signal.insert()
        # get rowid
        signals = SignalModel.get_rows("0")
        rowid = signals.all()[0].rowid
        # assert that there is one record
        self.assertEqual(signals.count(), 1)

        # prepare to test for pairs
        get_signal = SignalModel.find_by_rowid(rowid)
        ticker1 = get_signal.ticker1
        ticker2 = get_signal.ticker2
        get_signal.ticker_type = "pair"
        # update the signal
        get_signal.update(rowid)

        pair_to_search = ticker1 + "-" + ticker2

        # assert that there are same number of records of the ticker
        signals_list = SignalModel.get_list_ticker(pair_to_search, "0")
        self.assertEqual(len(signals_list), 1)

        # insert another signal to the database
        another_signal = SignalFactory()
        another_signal.ticker1 = ticker1
        another_signal.ticker2 = ticker2
        another_signal.ticker_type = "pair"
        another_signal.insert()

        # assert
        signals_list = SignalModel.get_list_ticker(pair_to_search, "0")
        self.assertEqual(len(signals_list), 2)
        signals_list = SignalModel.get_list_ticker(pair_to_search, "1")
        self.assertEqual(signals_list.count(), 1)

        # prepare to test for singles
        another_signal.ticker_type = "single"
        # update the signal
        another_signal.update(rowid)
        another_signal.update(rowid+1)

        # assert
        signals_list = SignalModel.get_list_ticker(ticker1, "0")
        self.assertEqual(len(signals_list), 2)
        signals_list = SignalModel.get_list_ticker(ticker1, "1")
        self.assertEqual(signals_list.count(), 1)

    def test_get_list_ticker_dates(self):
        """It should get a list of Signals for a given ticker name (pair or single) btw given dates"""

        test_signal = SignalFactory()

        # get all rows
        signals = SignalModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(signals.count(), 0)

        # insert one signal to the database
        test_signal.insert()
        # get rowid
        signals = SignalModel.get_rows("0")
        rowid = signals.all()[0].rowid
        # assert that there is one record
        self.assertEqual(signals.count(), 1)

        # prepare to test for pairs
        get_signal = SignalModel.find_by_rowid(rowid)
        ticker1 = get_signal.ticker1
        ticker2 = get_signal.ticker2
        get_signal.ticker_type = "pair"
        # update the signal
        get_signal.update(rowid)

        pair_to_search = ticker1 + "-" + ticker2
        date = get_signal.timestamp
        date1 = date - datetime.timedelta(hours=1)
        date2 = date + datetime.timedelta(hours=1)

        # assert that there are same number of records of the ticker
        signals_list = SignalModel.get_list_ticker_dates(
            pair_to_search, "0", date1, date2
        )
        self.assertEqual(len(signals_list), 1)

        # insert another signal to the database
        another_signal = SignalFactory()
        another_signal.ticker1 = ticker1
        another_signal.ticker2 = ticker2
        another_signal.timestamp = date + datetime.timedelta(minutes=5)
        another_signal.ticker_type = "pair"
        another_signal.insert()

        # assert
        signals_list = SignalModel.get_list_ticker_dates(
            pair_to_search, "0", date1, date2
        )
        self.assertEqual(len(signals_list), 2)
        signals_list = SignalModel.get_list_ticker_dates(
            pair_to_search, "1", date1, date2
        )
        self.assertEqual(signals_list.count(), 1)

        # prepare to test for singles
        another_signal.ticker_type = "single"
        # update the signal
        another_signal.update(rowid)
        another_signal.update(rowid+1)

        # assert
        signals_list = SignalModel.get_list_ticker_dates(ticker1, "0", date1, date2)
        self.assertEqual(len(signals_list), 2)
        signals_list = SignalModel.get_list_ticker_dates(ticker1, "1", date1, date2)
        self.assertEqual(signals_list.count(), 1)

    def test_get_list_status(self):
        """It should get a list of Signals for a given status"""

        test_signal = SignalFactory()

        # get all rows
        signals = SignalModel.get_rows("0")
        # assert that there are no records
        self.assertEqual(signals.count(), 0)

        # insert one signal to the database
        test_signal.insert()
        # get rowid
        signals = SignalModel.get_rows("0")
        rowid = signals.all()[0].rowid
        # assert that there is one record
        self.assertEqual(signals.count(), 1)

        # prepare to test
        get_signal = SignalModel.find_by_rowid(rowid)
        get_signal.order_status = "waiting"
        # update the signal
        get_signal.update(rowid)

        # assert that there are same number of records of the ticker
        signals_list = SignalModel.get_list_status("waiting", "0")
        self.assertEqual(len(signals_list), 1)

        # insert another signal to the database
        another_signal = SignalFactory()
        another_signal.order_status = "waiting"
        another_signal.insert()

        # assert
        signals_list = SignalModel.get_list_status("waiting", "0")
        self.assertEqual(len(signals_list), 2)
        signals_list = SignalModel.get_list_status("waiting", "1")
        self.assertEqual(signals_list.count(), 1)

        # prepare to test other status
        get_signal = SignalModel.find_by_rowid(rowid)
        get_signal.order_status = "filled"
        get_signal.update(rowid)
        get_signal = SignalModel.find_by_rowid(rowid+1)
        get_signal.order_status = "filled"
        get_signal.update(rowid+1)

        # assert
        signals_list = SignalModel.get_list_status("filled", "0")
        self.assertEqual(len(signals_list), 2)
        signals_list = SignalModel.get_list_status("filled", "1")
        self.assertEqual(signals_list.count(), 1)

    def test_check_ticker_status(self):
        """It should check pair and trade status"""

        test_ticker = TickerFactory()
        test_pair = PairFactory()
        test_signal = SignalFactory()

        ticker1 = "TEST1"
        ticker2 = "TEST2"
        hedge1 = 1.5

        # insert ticker to the database
        test_ticker.symbol = ticker1
        test_ticker.insert()

        # insert pair to the database
        test_pair.name = ticker1 + "-" + ticker2
        test_pair.ticker1 = ticker1
        test_pair.ticker2 = ticker2
        test_pair.hedge = hedge1
        test_pair.insert()

        # insert signal to the database
        test_signal.ticker1 = ticker1
        test_signal.ticker2 = ticker2
        test_signal.hedge_param = hedge1
        test_signal.ticker_type = "pair"
        test_signal.insert()

        # get rowid
        signals = SignalModel.get_rows("0")
        rowid = signals.all()[0].rowid

        # assert signal for passive pair
        self.assertFalse(test_signal.check_ticker_status())

        # assert signal for active pair
        test_pair.status = 1
        test_pair.update()
        self.assertTrue(test_signal.check_ticker_status())

        # assert signal for active pair with wrong hedge
        test_signal.hedge_param = 10
        test_signal.update(rowid)
        self.assertFalse(test_signal.check_ticker_status())

        # assert signal for passive single ticker
        test_signal.ticker_type = "single"
        test_signal.update(rowid)
        self.assertFalse(test_signal.check_ticker_status())

        # assert signal for active single ticker
        test_ticker.active = 1
        test_ticker.update(False)
        self.assertTrue(test_signal.check_ticker_status())

        # assert signal for pair not found
        test_signal.ticker1 = "NOT"
        test_signal.ticker2 = "FOUND"
        test_signal.ticker_type = "pair"
        test_signal.update(rowid)
        self.assertFalse(test_signal.check_ticker_status())

        # assert signal for ticker not found
        test_signal.ticker1 = "NOTFOUND"
        test_signal.ticker_type = "single"
        test_signal.update(rowid)
        self.assertFalse(test_signal.check_ticker_status())

    def test_split_ticker(self):
        """It should split the signal ticker string into ticker1, ticker2 and hedge parameter"""

        pair_equation_stk_true = [
            "NYSE:LNT",
            "NYSE:BF.A",
            "NYSE:LNT-NYSE:FTS*2.2",
            "NYSE:LNT-1.25*NYSE:FTS",
            "LNT-1.25*NYSE:FTS",
            "NYSE:LNT-NYSE:FTS",
            "BF.A-0.7*NYSE:BF.B",
        ]
        pair_equation_stk_false = [
            "0.7*NYSE:BF.A",
            "NYSE:LNT*2-NYSE:FTS",
            "NYSE:LNT-NYSE:FTS/3",
            "1.3*NYSE:LNT-NYSE:FTS*2.2",
            "LNT.#-3*FTS",
            "LNT-3*FTS-2*FTS",
        ]

        pair_equation_cash_true = [
            "USD.CAD",
            "USD.CAD-EUR.USD",
        ]

        pair_equation_cash_false = [
            "USDCAD",
            "EUR.JPY",
            "USDJPY-USD.CAD",
            "USDJPY-EUR.JPY",
        ]

        pair_equation_crypto_true = ["BTCUSD", "BTCUSD-SHIBUSD"]

        pair_equation_crypto_false = ["RRPUSD", "BTCUSD-RPEUR", "BTCUSD-RRPUSD"]

        tickers = [
            "LNT",
            "FTS",
            "BF.A",
            "BF.B",
            "USD.CAD",
            "EUR.USD",
            "EUR.JPY",
            "BTCUSD",
            "SHIBUSD",
            "RRPUSD",
        ]
        types = [
            "STK",
            "STK",
            "STK",
            "STK",
            "CASH",
            "CASH",
            "CASH",
            "CRYPTO",
            "CRYPTO",
            "CRYPTO",
        ]
        currencys = [
            "USD",
            "USD",
            "USD",
            "USD",
            "CAD",
            "USD",
            "EUR",
            "USD",
            "USD",
            "BTC",
        ]
        actives = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        # insert tickers to the database
        for n in range(len(tickers)):
            test_ticker = TickerFactory()
            test_ticker.symbol = tickers[n]
            test_ticker.sectype = types[n]
            test_ticker.currency = currencys[n]
            test_ticker.active = actives[n]
            test_ticker.insert()

        test_signal = SignalFactory()

        for item in pair_equation_stk_true:
            test_signal.ticker = item
            test_signal.insert()
            self.assertTrue(test_signal.splitticker())

        for item in pair_equation_stk_true:
            test_signal.ticker = item
            test_signal.insert()
            self.assertTrue(test_signal.splitticker())

        for item in pair_equation_stk_false:
            test_signal.ticker = item
            test_signal.insert()
            self.assertFalse(test_signal.splitticker())

        for item in pair_equation_cash_true:
            test_signal.ticker = item
            test_signal.insert()
            self.assertTrue(test_signal.splitticker())

        for item in pair_equation_cash_false:
            test_signal.ticker = item
            test_signal.insert()
            self.assertFalse(test_signal.splitticker())

        for item in pair_equation_crypto_true:
            test_signal.ticker = item
            test_signal.insert()
            self.assertTrue(test_signal.splitticker())

        for item in pair_equation_crypto_false:
            test_signal.ticker = item
            test_signal.insert()
            self.assertFalse(test_signal.splitticker())

    def test_get_avg_slip(self):
        """It should get the average slip of signals btw given dates"""

        expected_dic = {
            "buy": 2,
            "sell": 3,
            "avg": 2.5,
        }

        test_signal = SignalFactory()
        test_signal.timestamp = datetime.date.today()
        test_signal.ticker1 = "ticker1"
        test_signal.ticker2 = "ticker2"
        test_signal.ticker_type = "pair"
        test_signal.order_action = "buy"
        test_signal.slip = 1
        test_signal.insert()

        test_signal = SignalFactory()
        test_signal.timestamp = datetime.date.today()
        test_signal.ticker1 = "ticker1"
        test_signal.ticker2 = "ticker2"
        test_signal.ticker_type = "pair"
        test_signal.order_action = "buy"
        test_signal.slip = 3
        test_signal.insert()

        test_signal = SignalFactory()
        test_signal.timestamp = datetime.date.today()
        test_signal.ticker1 = "ticker1"
        test_signal.ticker2 = "ticker2"
        test_signal.ticker_type = "pair"
        test_signal.order_action = "sell"
        test_signal.slip = 2
        test_signal.insert()

        test_signal = SignalFactory()
        test_signal.timestamp = datetime.date.today()
        test_signal.ticker1 = "ticker1"
        test_signal.ticker2 = "ticker2"
        test_signal.ticker_type = "pair"
        test_signal.order_action = "sell"
        test_signal.slip = 4
        test_signal.insert()

        # get all rows
        signals = SignalModel.get_rows("0")
        # assert the number of rows
        self.assertEqual(signals.count(), 4)
        # get the first rowid
        rowid = signals.all()[0].rowid-3

        # get timestamp
        date1 = datetime.date.today() - datetime.timedelta(days=1)
        date2 = datetime.date.today() + datetime.timedelta(days=1)

        # assert pairs
        self.assertEqual(
            SignalModel.get_avg_slip("ticker1-ticker2", date1, date2), expected_dic
        )

        for i in range(0, 4):
            # get signals from the database
            signal = SignalModel.find_by_rowid(rowid+i)
            signal.ticker_type = "single"

        # assert pairs
        self.assertEqual(
            SignalModel.get_avg_slip("ticker1", date1, date2), expected_dic
        )

    def test_find_by_orderid(self):
        """It should get the most recent signal by order id"""

        test_signal = SignalFactory()
        test_signal.order_id1 = 101
        test_signal.order_id2 = 201
        test_signal.insert()

        test_signal = SignalFactory()
        test_signal.order_id1 = 101
        test_signal.order_id2 = 301
        test_signal.insert()

        # assert if it gets the most recent signal with order id
        signal = SignalModel.find_by_orderid(101)
        self.assertEqual(signal.order_id1, 101)

        # assert if it gets the most recent signal with order id
        signal = SignalModel.find_by_orderid(201)
        self.assertEqual(signal.order_id2, 201)

        # assert if it gets the most recent signal with order id
        signal = SignalModel.find_by_orderid(301)
        self.assertEqual(signal.order_id2, 301)

    def test_find_by_orderid_ticker(self):
        """It should get the signal by order id and ticker"""

        test_signal = SignalFactory()
        test_signal.ticker1 = "ticker1"
        test_signal.ticker2 = "ticker2"
        test_signal.order_id1 = 101
        test_signal.order_id2 = 201
        test_signal.insert()

        test_signal = SignalFactory()
        test_signal.ticker1 = "ticker1"
        test_signal.ticker2 = "ticker3"
        test_signal.order_id1 = 101
        test_signal.order_id2 = 301
        test_signal.insert()

        # assert if it gets the most recent signal with order id
        signal = SignalModel.find_by_orderid_ticker(101, "ticker1")
        self.assertEqual(signal.order_id1, 101)

        # assert if it gets the most recent signal with order id
        signal = SignalModel.find_by_orderid_ticker(201, "ticker2")
        self.assertEqual(signal.order_id2, 201)

        # assert if it gets no return
        signal = SignalModel.find_by_orderid_ticker(301, "ticker2")
        self.assertIsNone(signal)

    def test_check_latest(self):
        """used to get the latest signal with predefined statuses"""

        test_signal = SignalFactory()
        test_signal.insert()
        
        # get rowid
        signals = SignalModel.get_rows("0")
        rowid = signals.all()[0].rowid

        # assert if it gets no signal
        self.assertIsNone(SignalModel.check_latest())

        # change the order status
        test_signal.order_status = "waiting"
        test_signal.update(rowid)

        # assert if it gets the most recent waiting signal
        signal = SignalModel.check_latest()
        self.assertEqual(signal.order_status, "waiting")
