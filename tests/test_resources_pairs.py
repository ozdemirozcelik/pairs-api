"""
Test cases for Pair Resources
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
from models.pairs import PairModel
from models.tickers import TickerModel
from tests.factories import TickerFactory
from tests.factories import PairFactory
from resources.users import UserRegister

# rather than referring to an app directly, use a proxy,
# which points to the application handling the current activity
app.app_context().push()

DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///test.db")

BASE_URL = "/v4/pair"
GET_URL = "/v4/pairs/"
LOGIN_URL = "/v4/login"

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

    def _create_fake_tickers(self):
        """Adds 2 active 2 passive tickers to the database, returns 4 ticker symbols"""

        ticker_symbols = []

        # create a batch of tickers and insert to the database
        for ticker in TickerFactory.create_batch(4):
            ticker.insert()

        # get all tickers from the database
        selected_tickers = TickerModel.get_rows("0")

        # activate the first 2 tickers, and deactivate the remaining
        for i in range(2):
            selected_tickers[i].active = 1
            ticker_symbols.append(selected_tickers[i].symbol)
            selected_tickers[3 - i].active = 0
            ticker_symbols.append(selected_tickers[3 - i].symbol)
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

        return ticker_symbols

    ######################################################################
    #  TEST CASES
    ######################################################################

    ### POST METHOD ###

    def test_post_pair_created(self):
        """It should insert a Pair to the endpoint and assert that it exists"""

        test_pair = PairFactory()

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_pair_unauthorized(self):
        """It should try to insert a Pair to the endpoint with no fresh token"""

        test_pair = PairFactory()

        # assert with not fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(fresh=False),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_pair_bad_request_active_pair(self):
        """It should try to insert an active pair which a ticker is already active in another pair to the endpoint"""

        test_pair = PairFactory()

        # test active pair in another pair
        ticker_symbols = self._create_fake_tickers()
        test_pair.ticker1 = ticker_symbols[0]
        test_pair.status = 1

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_pair_bad_request_same_pair(self):
        """It should try to insert an existing pair to the endpoint"""

        test_pair = PairFactory()

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_pair_bad_request_problematic_ticker(self):
        """It should try to insert a problematic ticker symbol in a pair to the endpoint"""

        test_pair = PairFactory()
        test_pair.ticker1 = "P-T"

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("resources.pairs.PairModel.insert")
    def test_post_pair_server_error(self, mock_insert):
        """It should try to insert to the endpoint but an error occurs on the server side"""

        test_pair = PairFactory()

        # raise an exception during inserting to the database
        mock_insert.side_effect = Exception()

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    ### PUT METHOD ###

    def test_put_pair_update(self):
        """It should update and assert that it is updated"""

        test_pair = PairFactory()
        test_pair.name = test_pair.ticker1 + "-" + test_pair.ticker2

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_pair.hedge = 1.33

        # assert new creation with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test for exception handler for updating pair
        with mock.patch("resources.pairs.PairModel.update", side_effect=Exception):
            # assert create with fresh token
            response = self.client.put(
                BASE_URL,
                headers=self._get_headers(),
                json=test_pair.json(),
                content_type="application/json",
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # assert update with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["hedge"], 1.33)

    def test_put_pair_bad_request_active_pair(self):
        """It should try to activate pair in which a ticker is already active in another pair to the endpoint"""

        test_pair = PairFactory()

        # test active pair in another pair
        ticker_symbols = self._create_fake_tickers()
        test_pair.ticker1 = ticker_symbols[0]
        test_pair.status = 1

        # assert with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_pair_update_not_found(self):
        """It should try to update an unknown pair"""

        test_pair = PairFactory()

        # assert new creation with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ### GET METHOD ###

    def test_get_pair(self):
        """It should get a unique pair with details"""

        test_pair = PairFactory()
        test_pair.name = test_pair.ticker1 + "-" + test_pair.ticker2

        # add pair
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test for exception handler
        with mock.patch(
            "resources.pairs.PairModel.find_by_name", side_effect=Exception
        ):
            # get unique pair and assert
            response = self.client.get(BASE_URL + "/" + test_pair.name)
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # get unique pair and assert
        response = self.client.get(BASE_URL + "/" + test_pair.name)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], test_pair.name)

    def test_get_pair_not_found(self):
        """It should  try to get an unknow pair"""

        test_pair = PairFactory()
        test_pair.name = "UN-KNOWN"

        # add pair
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get unique pair and assert
        response = self.client.get(BASE_URL + "/" + test_pair.name)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_pairs(self):
        """It should get defined number of Pairs from the endpoint"""

        test_pair = PairFactory()

        # add pair
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get one pair and assert
        response = self.client.get(GET_URL + "0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["pairs"]), 1)

        test_pair = PairFactory()

        # add another pair
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get all pairs and assert
        response = self.client.get(GET_URL + "0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["pairs"]), 2)

        # test for exception handler
        with mock.patch("resources.pairs.PairModel.get_rows", side_effect=Exception):
            # get unique pair and assert
            response = self.client.get(GET_URL + "0")
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    ### DELETE METHOD ###

    def test_delete_pair(self):
        """It should delete the pair"""

        test_pair = PairFactory()
        test_pair.name = test_pair.ticker1 + "-" + test_pair.ticker2

        # add pair
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_pair.json(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + test_pair.name, headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'pair' deleted successfully.")

    def test_delete_pair_not_found(self):
        """It should try to delete but get not found return"""

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + "deletethis", headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "item not found.")

    def test_delete_pair_not_admin(self):
        """It should try to delete as a user (not admin) and get unauthorized return"""

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + "deletethis", headers=self._get_headers(user="user1")
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'admin' privilege required.")

    @patch("resources.pairs.PairModel.find_by_name")
    def test_put_pair_server_error(self, mock_delete):
        """It should try to delete pair from the endpoint but an error occurs on the server side"""

        # raise an exception during fetching from the database
        mock_delete.side_effect = Exception()

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + "deletethis", headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
