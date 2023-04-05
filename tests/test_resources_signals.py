"""
Test cases for Signal Resources
"""
import unittest
from unittest import mock
from unittest.mock import patch
import json
import os
from app import app
from db import db
from security import talisman, csrf
from flask_jwt_extended import create_access_token
from resources import status_codes as status
from models.signals import SignalModel
from models.pairs import PairModel
from models.tickers import TickerModel
from tests.factories import TickerFactory
from tests.factories import PairFactory
from tests.factories import SignalFactory
from resources.users import UserRegister

# rather than referring to an app directly, use a proxy,
# which points to the application handling the current activity
app.app_context().push()

DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///test.db")

BASE_URL = "/v4/signal"
HOOK_URL = "/v4/webhook"
ORDER_URL = "/v4/order"
GET_URL = "/v4/signals/"
LOGIN_URL = "/v4/login"

######################################################################
#  PAIR MODEL TEST CASES
######################################################################


class TestSignal(unittest.TestCase):
    """Test Cases for Signal Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.config["CSRF_DISABLE"] = True
        db.init_app(app)
        db.create_all()
        UserRegister.default_users()
        talisman.force_https = False
        csrf._csrf_disable = True

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.drop_all()

    def setUp(self):
        """This runs before each test"""
        db.session.query(TickerModel).delete()  # clean up the last tests
        db.session.query(PairModel).delete()  # clean up the last tests
        db.session.query(SignalModel).delete()  # clean up the last tests
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################
    def _get_headers(self, user="admin", fresh=True):
        """Get headers with token"""

        access_token = create_access_token(identity=user, fresh=fresh)

        headers = {"Authorization": "Bearer {}".format(access_token)}

        return headers

    def _create_fake_pairs(self, ticker1="A", ticker2="B", hedge=3):
        """Adds 1 pair to the database"""

        test_pair = PairFactory()

        test_pair.name = ticker1 + "-" + ticker2
        test_pair.ticker1 = ticker1
        test_pair.ticker2 = ticker2
        test_pair.hedge = str(hedge)
        test_pair.contracts = 10
        test_pair.status = 1

        test_pair.insert()

    def _create_fake_tickers(self, ticker1="A", ticker2="B"):
        """Adds 2 tickers to the database, first one is active"""

        test_ticker = TickerFactory()
        test_ticker.symbol = ticker1
        test_ticker.sectype = "STK"
        test_ticker.xch = "SMART"
        test_ticker.prixch = "NASDAQ"
        test_ticker.currency = "USD"
        test_ticker.active = 1

        test_ticker.insert()

        test_ticker = TickerFactory()
        test_ticker.symbol = ticker2
        test_ticker.sectype = "STK"
        test_ticker.xch = "SMART"
        test_ticker.prixch = "NASDAQ"
        test_ticker.currency = "USD"
        test_ticker.active = 0

        test_ticker.insert()

    def _create_fakes(self, ticker1="A", ticker2="B", hedge=3):
        """1 signal to the database"""

        # create new signal
        self._create_fake_tickers(ticker1, ticker2)
        self._create_fake_pairs(ticker1, ticker2, hedge)

        msg_body = {
            "passphrase": "webhook",
            "ticker": ticker1 + "-" + str(hedge) + "*" + ticker2,
            "order_action": "buy",
            "order_contracts": "100",
            "order_price": "1",
            "mar_pos": "long",
            "mar_pos_size": "100",
            "pre_mar_pos": "flat",
            "pre_mar_pos_size": "0",
            "order_comment": " Enter Long",
            "order_status": "waiting",
        }

        # assert with fresh token
        response = self.client.post(
            HOOK_URL, json=msg_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # get latest rowid
        signals = SignalModel.get_rows("0")
        rowid = signals.all()[0].rowid

        return msg_body, rowid

    ######################################################################
    #  TEST CASES
    ######################################################################

    ### POST METHOD ###

    def test_post_signal_active(self):
        """It should insert a Signal to the endpoint and assert that it exists"""

        self._create_fakes()

    def test_post_signal_not_active(self):
        """It should insert a Signal with not active ticker to the endpoint and assert that it exists"""

        msg_body, _ = self._create_fakes()
        msg_body["ticker"] = "B"

        # assert with fresh token
        response = self.client.post(
            HOOK_URL, json=msg_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_signal_create_prob_ticker(self):
        """It should insert a Signal with problematic ticker to the endpoint and assert that it exists"""

        new_body = SignalFactory().json()
        new_body["passphrase"] = "webhook"
        new_body.pop("timestamp")

        # assert not active ticker
        response = self.client.post(
            HOOK_URL, json=new_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_signal_create_wrong_pass(self):
        """It should try to insert a Signal with a wrong passphrase"""

        new_body = SignalFactory().json()
        new_body["passphrase"] = "wrongphrase"
        new_body.pop("timestamp")

        # assert with fresh token
        response = self.client.post(
            HOOK_URL, json=new_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_signal_create_bypass_status(self):
        """It should try to insert a Signal with a wrong passphrase"""

        new_body = SignalFactory().json()
        new_body["passphrase"] = "webhook"
        new_body.pop("timestamp")
        new_body["bypass_ticker_status"] = True

        # assert with fresh token
        response = self.client.post(
            HOOK_URL, json=new_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("resources.signals.SignalModel.splitticker")
    def test_post_pair_server_error(self, mock_split):
        """It should try to insert to the endpoint but an error occurs on the server side"""

        new_body = SignalFactory().json()
        new_body["passphrase"] = "webhook"
        new_body.pop("timestamp")

        # raise an exception during inserting to the database
        mock_split.side_effect = Exception()

        # assert with fresh token
        response = self.client.post(
            HOOK_URL, json=new_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    ### PUT METHOD ###

    def test_put_pair_update(self):
        """It should update and assert that it is updated"""

        msg_body, rowid = self._create_fakes()
        msg_body["rowid"] = rowid
        msg_body["order_status"] = "new_status"

        # assert update with fresh token
        response = self.client.put(
            HOOK_URL,
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["order_status"], "new_status")

        # test for exception handler for updating pair
        with mock.patch(
            "resources.signals.SignalModel.splitticker", side_effect=Exception
        ):
            # assert update with fresh token
            response = self.client.put(
                HOOK_URL,
                headers=self._get_headers(),
                json=msg_body,
                content_type="application/json",
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_put_pair_update_not_found(self):
        """It should try to update and assert an unknown signal that it is updated"""

        msg_body, rowid = self._create_fakes()
        msg_body["rowid"] = rowid+1

        # assert update with fresh token
        response = self.client.put(
            HOOK_URL,
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_pair_update_wrong_phrase(self):
        """It should try to update a Signal with a wrong passphrase"""

        msg_body, rowid = self._create_fakes()
        msg_body["rowid"] = rowid
        msg_body["passphrase"] = "wrongphrase"

        # assert update with fresh token
        response = self.client.put(
            HOOK_URL,
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    ### PUT METHOD ### ORDER UPDATES ###

    def test_put_pair_update_order_not_found(self):
        """It should try to update and assert an unknown signal that it is updated"""

        # create signal and update the orderid1 and orderid2
        msg_body, rowid = self._create_fakes()
        msg_body["rowid"] = rowid
        msg_body["order_id1"] = 100
        msg_body["order_id2"] = 101

        # assert update with fresh token
        response = self.client.put(
            HOOK_URL,
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["order_id1"], 100)

        # prepare for the order
        msg_body = {
            "passphrase": "webhook",
            "symbol": "A",
            "order_id": 200,
            "price": 41.45,
            "filled_qty": 90,
        }

        # assert order
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "item not found.")

    def test_put_pair_update_order(self):
        """It should update 1st and 2nd order and get a partially filled and then filled status."""

        # create signal and update the orderid1 and orderid2
        msg_body, rowid = self._create_fakes()
        msg_body["rowid"] = rowid
        msg_body["order_id1"] = 100
        msg_body["order_id2"] = 101

        # assert update with fresh token
        response = self.client.put(
            HOOK_URL,
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["order_id1"], 100)

        # prepare for the first order
        msg_body = {
            "passphrase": "webhook",
            "symbol": "A",
            "order_id": 100,
            "price": 41.45,
            "filled_qty": 90,
        }

        # assert 1st order
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["price1"], 41.45)

        # prepare for the second order
        msg_body = {
            "passphrase": "webhook",
            "symbol": "B",
            "order_id": 101,
            "price": 15.05,
            "filled_qty": 270,
        }

        # assert 2nd order
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["price2"], 15.05)
        self.assertEqual(data["order_status"], "part.filled")

        # prepare for order filled
        msg_body = {
            "passphrase": "webhook",
            "symbol": "B",
            "order_id": 101,
            "price": 15.05,
            "filled_qty": 300,
        }

        # assert 2nd order
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["price2"], 15.05)
        self.assertEqual(data["order_status"], "filled")

        # test for exception handler for updating pair
        with mock.patch("resources.signals.SignalModel.update", side_effect=Exception):
            # assert update with fresh token
            response = self.client.put(
                BASE_URL + "/order",
                headers=self._get_headers(),
                json=msg_body,
                content_type="application/json",
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # test with a wrong passphrase
        msg_body = {
            "passphrase": "wrongpassphrase",
            "symbol": "A",
            "order_id": 100,
            "price": 41.45,
            "filled_qty": 129,
        }

        # assert with wrong passphrase
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_pair_update_order_slip(self):
        """It should check if slip value is updated for a pair."""

        # create signal and update the orderid1 and orderid2
        msg_body, rowid = self._create_fakes()
         
        msg_body["rowid"] = rowid
        msg_body["order_price"] = 1
        msg_body["order_action"] = "sell"
        msg_body["order_id1"] = 100
        msg_body["order_id2"] = 101

        # assert update with fresh token
        response = self.client.put(
            HOOK_URL,
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["order_id1"], 100)

        # prepare for the first order
        msg_body = {
            "passphrase": "webhook",
            "symbol": "A",
            "order_id": 100,
            "price": 3,
            "filled_qty": 100,
        }

        # assert 1st order
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["price1"], 3)

        # prepare for the second order
        msg_body = {
            "passphrase": "webhook",
            "symbol": "B",
            "order_id": 101,
            "price": 1,
            "filled_qty": 300,
        }

        # assert 2nd order
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["slip"], -1)

    def test_put_pair_update_order_single(self):
        """It should update order details for a single ticker order."""

        # create signal and update the orderid1
        msg_body, rowid = self._create_fakes()
        msg_body["rowid"] = rowid
        msg_body["ticker"] = "A"
        msg_body["ticker1"] = "A"
        msg_body["ticker_type"] = "single"
        msg_body["order_action"] = "buy"
        msg_body["order_id1"] = 100

        # assert update with fresh token
        response = self.client.put(
            HOOK_URL,
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["order_id1"], 100)

        # prepare for the order details (partially filled)
        msg_body = {
            "passphrase": "webhook",
            "symbol": "A",
            "order_id": 100,
            "price": 2.5,
            "filled_qty": 90,
        }

        # assert order
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["price1"], 2.5)
        self.assertEqual(data["order_status"], "part.filled")

        # prepare for the order details (filled)
        msg_body = {
            "passphrase": "webhook",
            "symbol": "A",
            "order_id": 100,
            "price": 3,
            "filled_qty": 100,
        }

        # assert order
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["price1"], 3)
        self.assertEqual(data["order_status"], "filled")

    def test_put_pair_update_order_single_slip(self):
        """It should check if slip value is updated for a single ticker order."""

        # create signal and update the orderid1
        msg_body, rowid = self._create_fakes()
        msg_body["rowid"] = rowid
        msg_body["ticker"] = "A"
        msg_body["ticker1"] = "A"
        msg_body["ticker_type"] = "single"
        msg_body["order_action"] = "sell"
        msg_body["order_price"] = 100
        msg_body["order_id1"] = 100

        # assert update with fresh token
        response = self.client.put(
            HOOK_URL,
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["order_id1"], 100)

        # prepare for the order details (partially filled)
        msg_body = {
            "passphrase": "webhook",
            "symbol": "A",
            "order_id": 100,
            "price": 99,
            "filled_qty": 100,
        }

        # assert order
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["slip"], -1)

    def test_put_pair_update_order_cancel(self):
        """It should cancel the order by changing the order status for a defined order_id and symbol"""

        # create signal and update the orderid1 and orderid2
        msg_body, rowid = self._create_fakes()
        msg_body["rowid"] = rowid
        msg_body["order_id1"] = 100
        msg_body["order_id2"] = 101

        # assert update with fresh token
        response = self.client.put(
            HOOK_URL,
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["order_id1"], 100)

        # update with the order details
        msg_body = {
            "passphrase": "webhook",
            "cancel": True,
            "symbol": "A",
            "order_id": 100,
            "price": -1,  # assign any value
            "filled_qty": -1,  # assign any value
        }

        # assert update with fresh token
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["order_status"], "canceled")

    def test_put_pair_update_order_partial(self):
        """It should cancel the order by changing the order status for a defined order_id and symbol"""

        # create signal and update the orderid1 and orderid2
        msg_body, rowid = self._create_fakes()
        msg_body["rowid"] = rowid
        msg_body["order_id1"] = 100
        msg_body["order_id2"] = 101

        # assert update with fresh token
        response = self.client.put(
            HOOK_URL,
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["order_id1"], 100)

        # update with the partial order details
        # tey without order_contracts
        msg_body = {
            "passphrase": "webhook",
            "partial": True,
            "symbol": "A",
            "order_id": 100,
            "price": -1,  # assign any value
            "filled_qty": -1,  # assign any value
        }

        # assert update with fresh token
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # update with the order details
        msg_body["order_contracts"] = 50

        # assert update with fresh token
        response = self.client.put(
            BASE_URL + "/order",
            headers=self._get_headers(),
            json=msg_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["order_status"], "part.filled")

    ### GET METHOD ###
    def test_get_signal(self):
        """It should get a unique signal with details"""

        # create 2 signals
        self._create_fakes()
        _, rowid = self._create_fakes(ticker1="C", ticker2="D", hedge=3)

        # get unique pair and assert
        response = self.client.get(BASE_URL + "/" + str(rowid))
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["ticker1"], "C")

        # test for exception handler to get pair
        with mock.patch(
            "resources.signals.SignalModel.find_by_rowid", side_effect=Exception
        ):
            # assert get with fresh token
            response = self.client.get(BASE_URL + "/" + "2")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_get_signal_not_found(self):
        """It should try to get an unknown signal"""

        _, rowid = self._create_fakes()

        # assert get with fresh token
        response = self.client.get(BASE_URL + "/" + str(rowid+1))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_signal_list(self):
        """It should get defined number of signal with details"""

        # insert a batch of signals to the database
        for signal in SignalFactory.create_batch(3):
            signal.insert()

        # get all signals without authorization header
        response = self.client.get(GET_URL + "0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["signals"]), 3)

        # get 3 signals
        response = self.client.get(GET_URL + "2")
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["signals"]), 2)

        # test for exception handler to get pair
        with mock.patch(
            "resources.signals.SignalModel.get_rows", side_effect=Exception
        ):
            # assert get with fresh token
            response = self.client.get(GET_URL + "0")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_get_signal_list_auth(self):
        """It should try to get all signals but should receive a max of 5"""

        # insert a batch of signals to the database
        for signal in SignalFactory.create_batch(7):
            signal.insert()

        # get all signals without authorization header
        response = self.client.get(GET_URL + "0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["signals"]), 5)

        # get all signals with authorization header
        response = self.client.get(
            GET_URL + "0",
            headers=self._get_headers(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["signals"]), 7)

    def test_get_signals_ticker(self):
        """It should get defined number of signals for a specific ticker"""

        # create 2 signals
        self._create_fakes()
        msg_body, rowid = self._create_fakes(ticker1="C", ticker2="D", hedge=3)

        # create 3rd signal with the same ticker
        response = self.client.post(
            HOOK_URL, json=msg_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # get signals with ticker without authorization header
        response = self.client.get(GET_URL + "ticker/C-D/0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["signals"]), 2)

        # get 3 signals
        response = self.client.get(GET_URL + "ticker/C-D/1")
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["signals"]), 1)

        # test for exception handler to get pair
        with mock.patch(
            "resources.signals.SignalModel.get_list_ticker", side_effect=Exception
        ):
            # assert get with fresh token
            response = self.client.get(GET_URL + "ticker/C-D/1")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_get_signals_status(self):
        """It should get defined number of signals for a specific status"""

        # insert a batch of signals to the database
        for signal in SignalFactory.create_batch(4):
            signal.order_status = "waiting"
            signal.insert()

        # get signals with ticker without authorization header
        response = self.client.get(GET_URL + "status/waiting/0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["signals"]), 4)

        # get 1 signal
        response = self.client.get(GET_URL + "status/waiting/1")
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["signals"]), 1)

        # get 0 signals
        response = self.client.get(GET_URL + "status/otherstatus/0")
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["signals"]), 0)

        # test for exception handler to get pair
        with mock.patch(
            "resources.signals.SignalModel.get_list_status", side_effect=Exception
        ):
            # assert get with fresh token
            response = self.client.get(GET_URL + "status/waiting/1")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    ### DELETE METHOD ###

    def test_delete_signal(self):
        """It should delete the signal"""

        # create 1 signal
        _, rowid = self._create_fakes()

        # delete and assert
        response = self.client.delete(BASE_URL + "/" + str(rowid), headers=self._get_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'signal' deleted successfully.")

    def test_delete_signal_not_found(self):
        """It should try to delete but get not found return"""

        # delete and assert
        response = self.client.delete(BASE_URL + "/1", headers=self._get_headers())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "item not found.")

    def test_delete_signal_not_admin(self):
        """It should try to delete as a user (not admin) and get unauthorized return"""

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + "deletethis", headers=self._get_headers(user="user1")
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'admin' privilege required.")

    @patch("resources.signals.SignalModel.find_by_rowid")
    def test_put_pair_server_error(self, mock_delete):
        """It should try to delete signal from the endpoint but an error occurs on the server side"""

        # raise an exception during fetching from the database
        mock_delete.side_effect = Exception()

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + "deletethis", headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
