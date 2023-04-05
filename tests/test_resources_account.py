"""
Test cases for Account Resources
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
from models.account import AccountModel
from tests.factories import AccountFactory
from resources.users import UserRegister


# rather than referring to an app directly, use a proxy,
# which points to the application handling the current activity
app.app_context().push()

DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///test.db")

BASE_URL = "/v4/pnl"
LOGIN_URL = "/v4/login"

######################################################################
#  ACCOUNT MODEL TEST CASES
######################################################################


class TestAccount(unittest.TestCase):
    """Test Cases for Account Model"""

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
        db.session.query(AccountModel).delete()  # clean up the last tests
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

    ######################################################################
    #  TEST CASES
    ######################################################################

    ### POST METHOD ###

    def test_post_PNL_created(self):
        """It should insert a PNL to the endpoint and assert that it exists"""

        new_body = AccountFactory().json()
        new_body["passphrase"] = "webhook"
        new_body.pop("timestamp")

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=new_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_PNL_created_wrong_pass(self):
        """It should try to insert a PNL to the endpoint with wrong passphrase"""

        new_body = AccountFactory().json()
        new_body["passphrase"] = "wrongpass"
        new_body.pop("timestamp")

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=new_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("resources.account.AccountModel.insert")
    def test_post_PNL_server_error(self, mock_insert):
        """It should try to insert to the endpoint but an error occurs on the server side"""

        new_body = AccountFactory().json()
        new_body["passphrase"] = "webhook"
        new_body.pop("timestamp")

        # raise an exception during inserting to the database
        mock_insert.side_effect = Exception()

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=new_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_put_PNL_update(self):
        """It should update a PNL to the endpoint and assert that it exists"""

        # insert an account
        new_body = AccountFactory().json()
        new_body["passphrase"] = "webhook"
        new_body.pop("timestamp")

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=new_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get rowid
        account = AccountModel.get_rows("0")
        rowid = account.all()[0].rowid
        self.assertEqual(account.count(), 1)      

        # update an account
        new_body["rowid"] = rowid
        new_body["RealizedPnL"] = 333

        # assert with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=new_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["RealizedPnL"], 333)

        # test for exception handler for updating account
        with mock.patch("resources.account.AccountModel.update", side_effect=Exception):
            # assert create with fresh token
            response = self.client.put(
                BASE_URL,
                headers=self._get_headers(),
                json=new_body,
                content_type="application/json",
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # try to update an account with wrong pass
        new_body["rowid"] = 1
        new_body["RealizedPnL"] = 333
        new_body["passphrase"] = "wrongpass"

        # assert with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=new_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_PNL_update_not_found(self):
        """It should update a PNL to the endpoint and assert that it exists"""

        # insert an account
        new_body = AccountFactory().json()
        new_body["rowid"] = 1
        new_body["passphrase"] = "webhook"
        new_body.pop("timestamp")

        # assert with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=new_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "item not found.")

    ### GET METHOD ###

    def test_get_PNL(self):
        """It should get PNLs from the endpoint with rowid"""

        new_body = AccountFactory().json()
        new_body["passphrase"] = "webhook"
        new_body["BuyingPower"] = 1111
        new_body.pop("timestamp")

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=new_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # get rowid
        account = AccountModel.get_rows("0")
        rowid = account.all()[0].rowid
        self.assertEqual(account.count(), 1)      

        # get account
        response = self.client.get(BASE_URL + "/" + str(rowid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["BuyingPower"], 1111)

    def test_get_PNL_not_found(self):
        """It should try to get an unknown PNL"""

        # get account
        response = self.client.get(BASE_URL + "/1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "item not found.")

    def test_get_PNLs_auth(self):
        """It should get number of PNLs with authorization header"""

        # insert a batch of PNLs to the database
        for pnl in AccountFactory.create_batch(7):
            pnl.insert()

        # get accounts
        response = self.client.get(
            BASE_URL + "s/0",
            headers=self._get_headers(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["pnls"]), 7)

    def test_get_PNLs_no_auth(self):
        """It should get number of PNLs without authorization header"""

        # insert a batch of PNLs to the database
        for pnl in AccountFactory.create_batch(7):
            pnl.insert()

        # get accounts
        response = self.client.get(BASE_URL + "s/7")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["pnls"]), 5)

        # get accounts
        response = self.client.get(BASE_URL + "s/0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["pnls"]), 5)

    @patch("resources.account.AccountModel.get_rows")
    def test_get_PNLs_server_error(self, mock_rows):
        """It should try to insert to the endpoint but an error occurs on the server side"""

        # raise an exception during inserting to the database
        mock_rows.side_effect = Exception()

        # assert with fresh token
        response = self.client.get(BASE_URL + "s/0")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch("resources.account.AccountModel.find_by_rowid")
    def test_get_PNL_server_error(self, mock_find):
        """It should try to insert to the endpoint but an error occurs on the server side"""

        # raise an exception during inserting to the database
        mock_find.side_effect = Exception()

        # assert with fresh token
        response = self.client.get(BASE_URL + "/1")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    ### DELETE METHOD ###

    def test_delete_PNL(self):
        """It should delete the PNL"""

        # add new PNL
        new_body = AccountFactory().json()
        new_body["passphrase"] = "webhook"
        new_body.pop("timestamp")

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=new_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # get rowid
        account = AccountModel.get_rows("0")
        rowid = account.all()[0].rowid
        self.assertEqual(account.count(), 1)     

        # test for exception handler
        with mock.patch(
            "resources.account.AccountModel.find_by_rowid", side_effect=Exception
        ):
            # delete and assert
            response = self.client.delete(BASE_URL + "/" + str(rowid), headers=self._get_headers())
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # delete and assert
        response = self.client.delete(BASE_URL + "/" + str(rowid), headers=self._get_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'pnl' deleted successfully.")

    def test_delete_PNL_not_admin(self):
        """It should try to delete as a user (not admin) and get unauthorized return"""

        new_body = AccountFactory().json()
        new_body["passphrase"] = "webhook"
        new_body.pop("timestamp")
        
        # assert with fresh token
        response = self.client.delete(
            BASE_URL + "/1", headers=self._get_headers(user="user1")
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'admin' privilege required.")

    def test_delete_PNL_not_found(self):
        """It should try to delete but get not found return"""

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/1", headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "item not found.")
