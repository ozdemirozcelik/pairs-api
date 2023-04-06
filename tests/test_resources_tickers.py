"""
Test cases for Ticker Resources
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
from models.tickers import TickerModel
from models.pairs import PairModel
from tests.factories import TickerFactory
from tests.factories import PairFactory
from resources.users import UserRegister

# rather than referring to an app directly, use a proxy,
# which points to the application handling the current activity
app.app_context().push()

DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///test.db")

BASE_URL = "/v4/ticker"
GET_URL = "/v4/tickers/"
LOGIN_URL = "/v4/login"

######################################################################
#  TICKER RESOURCETEST CASES
######################################################################


class TestTicker(unittest.TestCase):
    """Test Cases for Ticker Resource"""

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

    def _create_fake_pairs(self):
        """Adds 4 pairs to the database with 2 active 2 passive pairs, returns 4 ticker1 names"""

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

        return ticker1_names

    ######################################################################
    #  TEST CASES
    ######################################################################

    ### POST METHOD ###

    def test_post_ticker_created(self):
        """It should insert a Ticker to the endpoint and assert that it exists"""

        test_ticker = TickerFactory()

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_ticker_unauthorized(self):
        """It should try to insert a Ticker to the endpoint with no fresh token"""

        test_ticker = TickerFactory()

        # assert with not fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(fresh=False),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_ticker_bad_request_active_ticker(self):
        """It should try to insert an active ticker which is already active in another pair to the endpoint"""

        test_ticker = TickerFactory()

        # test active ticker in another pair
        ticker1_names = self._create_fake_pairs()
        test_ticker.symbol = ticker1_names[0]
        test_ticker.active = 1

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_ticker_bad_request_same_ticker(self):
        """It should try to insert an existing ticker to the endpoint"""

        test_ticker = TickerFactory()

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("resources.tickers.TickerModel.insert")
    def test_post_ticker_server_error(self, mock_insert):
        """It should try to insert to the endpoint but an error occurs on the server side"""

        test_ticker = TickerFactory()

        # raise an exception during inserting to the database
        mock_insert.side_effect = Exception()

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    ### PUT METHOD ###

    def test_put_ticker_create_and_update(self):
        """It should insert a new Ticker to the endpoint then update and assert that it is updated"""

        test_ticker = TickerFactory()

        # test for exception handler for creating new ticker
        with mock.patch("resources.tickers.TickerModel.insert", side_effect=Exception):
            # assert create with fresh token
            response = self.client.put(
                BASE_URL,
                headers=self._get_headers(),
                json=test_ticker.json(),
                content_type="application/json",
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # assert new creation with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_ticker.order_type = "NEW_ORDER_TYPE"

        # test for exception handler for updating ticker
        with mock.patch("resources.tickers.TickerModel.update", side_effect=Exception):
            # assert create with fresh token
            response = self.client.put(
                BASE_URL,
                headers=self._get_headers(),
                json=test_ticker.json(),
                content_type="application/json",
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # assert update with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["order_type"], "NEW_ORDER_TYPE")

    def test_put_ticker_unauthorized(self):
        """It should try to insert a Ticker to the endpoint with no fresh token"""

        test_ticker = TickerFactory()

        # assert with not fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(fresh=False),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_ticker_bad_request_active_ticker(self):
        """It should try to insert an active ticker which is already active in another pair to the endpoint"""

        test_ticker = TickerFactory()

        # test active ticker in another pair
        ticker1_names = self._create_fake_pairs()
        test_ticker.symbol = ticker1_names[0]
        test_ticker.active = 1

        # assert with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_pnl_update(self):
        """It should update PNL and assert that it is updated"""

        test_ticker = TickerFactory()
        # assert new creation with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_body = test_ticker.json()
        new_body["passphrase"] = "webhook"
        new_body["active_pos"] = -100.1

        # test for exception handler
        with mock.patch("resources.tickers.TickerModel.update", side_effect=Exception):
            # assert create with fresh token
            response = self.client.put(
                BASE_URL + "/pnl", json=new_body, content_type="application/json"
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # assert PNL update with fresh token
        response = self.client.put(
            BASE_URL + "/pnl", json=new_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["active_pos"], -100.1)

    def test_put_pnl_update_wrong_pass(self):
        """It should try to update PNL with a wrong passphrase and get bad request"""

        test_ticker = TickerFactory()
        # assert new creation with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_body = test_ticker.json()
        new_body["passphrase"] = "wrongpass"

        # assert PNL update with wrong passphrase
        response = self.client.put(
            BASE_URL + "/pnl", json=new_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "incorrect passphrase.")

    def test_put_pnl_update_not_found(self):
        """It should try to update PNL with unknown ticker and gets not found response"""

        test_ticker = TickerFactory()
        new_body = test_ticker.json()
        new_body["passphrase"] = "webhook"

        # assert PNL update with wrong passphrase
        response = self.client.put(
            BASE_URL + "/pnl", json=new_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "item not found.")

    ### GET METHOD ###

    def test_get_ticker(self):
        """It should get a unique ticker details"""

        test_ticker = TickerFactory()
        symbol = test_ticker.symbol

        # add ticker
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get unique ticker and assert
        response = self.client.get(BASE_URL + "/" + symbol)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["symbol"], symbol)

        # test for exception handler
        with mock.patch(
            "resources.tickers.TickerModel.find_by_symbol", side_effect=Exception
        ):
            # get unique ticker and assert
            response = self.client.get(BASE_URL + "/" + symbol)
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_get_ticker_not_found(self):
        """It should get not found return"""

        # get unique ticker and assert
        response = self.client.get(BASE_URL + "/" + "tickername")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_tickers(self):
        """It should get defined number of Tickers from the endpoint"""

        test_ticker = TickerFactory()

        # add ticker
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get one ticker and assert
        response = self.client.get(GET_URL + "0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["tickers"]), 1)

        test_ticker = TickerFactory()

        # add another ticker
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get all tickers and assert
        response = self.client.get(GET_URL + "0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["tickers"]), 2)

        # test for exception handler
        with mock.patch(
            "resources.tickers.TickerModel.get_rows", side_effect=Exception
        ):
            # get unique ticker and assert
            response = self.client.get(GET_URL + "0")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @patch("resources.tickers.TickerModel.get_rows")
    def test_put_ticker_server_error(self, mock_get_rows):
        """It should try to get ticker from the endpoint but an error occurs on the server side"""

        # raise an exception during fetching from the database
        mock_get_rows.side_effect = Exception()

        # get all tickers and assert
        response = self.client.get(GET_URL + "0")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    ### DELETE METHOD ###

    def test_delete_ticker(self):
        """It should delete the ticker"""

        test_ticker = TickerFactory()

        # add ticker
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_ticker.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + test_ticker.symbol, headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'ticker' deleted successfully.")

    def test_delete_ticker_not_found(self):
        """It should try to delete but get not found return"""

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + "deletethis", headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "item not found.")

    def test_delete_ticker_not_admin(self):
        """It should try to delete as a user (not admin) and get unauthorized return"""

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + "deletethis", headers=self._get_headers(user="user1")
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'admin' privilege required.")

    @patch("resources.tickers.TickerModel.find_by_symbol")
    def test_delete_ticker_server_error(self, mock_delete):
        """It should try to delete ticker from the endpoint but an error occurs on the server side"""

        # raise an exception during fetching from the database
        mock_delete.side_effect = Exception()

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + "deletethis", headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
