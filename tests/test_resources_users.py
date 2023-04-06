"""
Test cases for User Resources
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
from services.resources import status_codes as status
from services.models.users import UserModel
from services.models.session import SessionModel
from tests.factories import UserFactory
from tests.factories import SessionFactory
from services.resources.users import UserRegister

# rather than referring to an app directly, use a proxy,
# which points to the application handling the current activity
app.app_context().push()
app.test_request_context().push()

DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///test.db")

BASE_URL = "/v4/user"
GET_URL = "/v4/users/"
LOGIN_URL = "/v4/login"
LOGOUT_URL = "/v4/logout"
REFRESH_URL = "/v4/refresh"

######################################################################
#  USER RESOURCE TEST CASES
######################################################################


class TestUser(unittest.TestCase):
    """Test Cases for User Resource"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.config["CSRF_DISABLE"] = True
        db.init_app(app)
        db.create_all()
        talisman.force_https = False
        csrf._csrf_disable = True

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        db.session.query(UserModel).delete()  # clean up the last tests
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

    # def test_add_default_users(self):
    #     """It should insert default users and assert that it exists"""
    #
    #     db.session.query(UserModel).delete()  # clean up the current users
    #     UserRegister.default_users()
    #

    def test_post_user_created(self):
        """It should insert a User to the endpoint and assert that it exists"""

        test_user = UserFactory().json()
        test_user["password"] = "test"

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_user_unauthorized(self):
        """It should try to insert a User with not fresh token"""

        test_user = UserFactory().json()
        test_user["password"] = "test"

        # assert with not fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(fresh=False),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_user_not_admin(self):
        """It should try to insert a User without admin rights"""

        test_user = UserFactory().json()
        test_user["password"] = "test"

        # assert with no admin rights
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(user="user"),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_existing_user(self):
        """It should try to insert an existing username"""

        test_user = UserFactory().json()
        test_user["username"] = "user1"
        test_user["password"] = "test"

        # insert 1st user
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # try to insert the same user
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("services.resources.users.UserModel.insert")
    def test_post_user_server_error(self, mock_insert):
        """It should try to insert to the endpoint but an error occurs on the server side"""

        test_user = UserFactory().json()
        test_user["password"] = "test"

        # raise an exception during inserting to the database
        mock_insert.side_effect = Exception()

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_post_login(self):
        """It should login and get authentication token"""

        UserRegister.default_users()

        test_user = UserFactory().json()
        test_user["username"] = "admin"
        test_user["password"] = "password"
        test_user["expire"] = 10

        # test for exception handler for creating new user
        with mock.patch("services.models.session.SessionModel.insert", side_effect=Exception):
            # try to login
            response = self.client.post(
                LOGIN_URL, json=test_user, content_type="application/json"
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # post and assert login
        response = self.client.post(
            LOGIN_URL, json=test_user, content_type="application/json"
        )
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(data["access_token"])
        self.assertEqual(data["expire"], 10)

    def test_post_login_unauthorized(self):
        """It should try login with wrong credentials"""

        UserRegister.default_users()

        test_user = UserFactory().json()
        test_user["username"] = "fake"
        test_user["password"] = "password"
        test_user["expire"] = 10

        # post and assert login
        response = self.client.post(
            LOGIN_URL, json=test_user, content_type="application/json"
        )
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(data["message"], "Invalid Credentials!")

    ## TODO: works in conda virtual env., not working in python virtual env.
    # @patch("services.resources.users.request")
    # @patch("services.models.session.SessionModel.find_by_value")
    # def test_post_logout(self, mock_cookie, mock_session):
    #     """It should logout"""
    # 
    #     mock_cookie.cookies.get.return_value = True
    #     # test if session delete is called
    #     self.assertTrue(mock_session.delete, "delete is called")
    # 
    #     # post and assert logout
    #     response = self.client.post(LOGOUT_URL, headers=self._get_headers())
    #     data = json.loads(response.get_data(as_text=True))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(data["message"], "Successfully logged out")

    def test_post_refresh_token(self):
        """It should refresh tokens"""
        UserRegister.default_users()

        test_user = UserFactory().json()
        test_user["username"] = "admin"
        test_user["password"] = "password"
        test_user["expire"] = 10

        # post and assert login
        response = self.client.post(
            LOGIN_URL, json=test_user, content_type="application/json"
        )
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(data["refresh_token"])
        self.assertEqual(data["expire"], 10)

        header = {"Authorization": "Bearer {}".format(data["refresh_token"])}

        # post and assert login
        response = self.client.post(REFRESH_URL, headers=header)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(data["refresh_token"])

    ### PUT METHOD ###

    def test_put_user_create_and_update(self):
        """It should insert a new User to the endpoint then update and assert that it is updated"""

        test_user = UserFactory().json()
        username = test_user["username"]
        test_user["password"] = "test"

        # test for exception handler for creating new user
        with mock.patch("services.resources.users.UserModel.insert", side_effect=Exception):
            # assert create with fresh token
            response = self.client.put(
                BASE_URL,
                headers=self._get_headers(),
                json=test_user,
                content_type="application/json",
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # assert new creation with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test for exception handler for updating user
        with mock.patch("services.resources.users.UserModel.update", side_effect=Exception):
            # assert create with fresh token
            response = self.client.put(
                BASE_URL,
                headers=self._get_headers(),
                json=test_user,
                content_type="application/json",
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # assert update with fresh token
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["username"], username)

    def test_put_user_not_admin(self):
        """It should try to insert a User without admin rights"""

        test_user = UserFactory().json()
        test_user["password"] = "test"

        # assert with no admin rights
        response = self.client.put(
            BASE_URL,
            headers=self._get_headers(user="user"),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    ### GET METHOD ###

    def test_get_user(self):
        """It should get a unique user details - currently no details"""

        test_user = UserFactory().json()
        username = test_user["username"]
        test_user["password"] = "test"

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get unique user and assert
        response = self.client.get(
            BASE_URL + "/" + username, headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["username"], username)

        # test for exception handler
        with mock.patch(
            "services.resources.users.UserModel.find_by_username", side_effect=Exception
        ):
            # get unique user and assert
            response = self.client.get(
                BASE_URL + "/" + username, headers=self._get_headers()
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_get_user_no_admin(self):
        """It should get a unique user details - currently no details"""

        test_user = UserFactory().json()
        username = test_user["username"]
        test_user["password"] = "test"

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get unique user and assert
        response = self.client.get(
            BASE_URL + "/" + username, headers=self._get_headers(user="user1")
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'admin' privilege required.")

    def test_get_user_not_found(self):
        """It should get not found return"""

        # get unique user and assert
        response = self.client.get(
            BASE_URL + "/nonexistinguser", headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "item not found.")

    @patch("services.resources.users.UserModel.get_rows")
    def test_put_user_server_error(self, mock_get_rows):
        """It should try to get user from the endpoint but an error occurs on the server side"""

        # raise an exception during fetching from the database
        mock_get_rows.side_effect = Exception()

        # get all users and assert
        response = self.client.get(GET_URL + "0", headers=self._get_headers())
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_users(self):
        """It should get defined number of users"""

        # create a batch of users and insert to the database
        for user in UserFactory.create_batch(3):
            user.insert()

        # get users and assert
        response = self.client.get(GET_URL + "0", headers=self._get_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data["users"]), 3)

        # test for exception handler
        with mock.patch("services.resources.users.UserModel.get_rows", side_effect=Exception):
            # get unique user and assert
            response = self.client.get(GET_URL + "0", headers=self._get_headers())
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def test_get_users_no_admin(self):
        """It should try to get defined number of users without admin rights"""

        # create a batch of users and insert to the database
        for user in UserFactory.create_batch(3):
            user.insert()

        # get users and assert
        response = self.client.get(
            GET_URL + "0", headers=self._get_headers(user="user1")
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'admin' privilege required.")

    ### DELETE METHOD ###

    def test_delete_user(self):
        """It should delete the user"""

        test_user = UserFactory().json()
        username = test_user["username"]
        test_user["password"] = "test"

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test for exception handler
        with mock.patch(
            "services.resources.users.UserModel.find_by_username", side_effect=Exception
        ):
            # delete unique user and assert
            response = self.client.delete(
                BASE_URL + "/" + username, headers=self._get_headers()
            )
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + username, headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'user' deleted successfully.")

    def test_delete_user_not_found(self):
        """It should try to delete but get not found return"""

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + "deletethis", headers=self._get_headers()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "item not found.")

    def test_delete_user_not_admin(self):
        """It should try to delete as a user (not admin) and get unauthorized return"""

        test_user = UserFactory().json()
        username = test_user["username"]
        test_user["password"] = "test"

        # assert with fresh token
        response = self.client.post(
            BASE_URL,
            headers=self._get_headers(),
            json=test_user,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # delete and assert
        response = self.client.delete(
            BASE_URL + "/" + username, headers=self._get_headers(user="user1")
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["message"], "'admin' privilege required.")
