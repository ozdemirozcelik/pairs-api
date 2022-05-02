from datetime import timedelta
from flask_restful import Resource, reqparse
from models.users import UserModel
from blacklist import BLACKLIST
from hmac import compare_digest
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required
)

_parser = reqparse.RequestParser()
_parser.add_argument('username',
                     type=str,
                     required=True,
                     help="Username cannot be empty!"
                     )
_parser.add_argument('password',
                     type=str,
                     required=True,
                     help="Password cannot be empty!"
                     )
_parser.add_argument('expire',
                     type=int,
                     default=10
                     )


class UserRegister(Resource):

    @staticmethod
    def default_users():
        # Add Default Users
        if not UserModel.find_by_username("admin"):
            admin = UserModel("admin", "123")
            admin.insert()
        if not UserModel.find_by_username("user1"):
            user = UserModel("user1", "123")
            user.insert()

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def post():

        claims = get_jwt()

        # TODO: Register only if admin
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401  # Return Unauthorized

        data = _parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "Username is already in use"}, 400  # Return Bad Request

        item = UserModel(data['username'], data['password'])

        try:
            item.insert()

        except Exception as e:
            print('Error occurred - ', e)  # better log the errors
            return {"message": "An error occurred inserting the item."}, 500  # Return Interval Server Error

        return {"message": "User created successfully."}, 201  # Return Successful Creation of Resource

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def put():

        claims = get_jwt()

        # TODO: Update only if admin
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401  # Return Unauthorized

        data = _parser.parse_args()

        item = UserModel(data['username'], data['password'])

        if UserModel.find_by_username(data['username']):
            try:
                item.update()

            except Exception as e:
                print('Error occurred - ', e)
                return {"message": "An error occurred updating the item."}, 500  # Return Interval Server Error

            return item.json()

        try:
            item.insert()

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred inserting the item."}, 500  # Return Interval Server Error

        return {"message": "User created successfully."}, 201  # Return Successful Creation of Resource


class UserList(Resource):

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def get(number_of_users="0"):

        claims = get_jwt()

        # TODO: List only if admin
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401  # Return Unauthorized

        try:
            users = UserModel.get_rows(number_of_users)

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while getting the users."}, 500  # Return Interval Server Error

        # return {'users': list(map(lambda x: x.json(), users))}  # we can map the list of objects,
        return {'users': [user.json() for user in users]}  # but this one is slightly more readable


class User(Resource):

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def get(username):

        claims = get_jwt()

        # TODO: Show only if admin
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401  # Return Unauthorized

        try:
            item = UserModel.find_by_username(username)

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while getting the user."}, 500  # Return Interval Server Error

        if item:
            return item.json()

        return {'message': 'User not found'}, 404  # Return Not Found

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def delete(username):

        claims = get_jwt()

        # TODO: Delete only if admin
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401  # Return Unauthorized

        try:
            UserModel.delete(username)

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while deleting the user."}, 500  # Return Interval Server Error

        return {'message': 'User deleted'}


class UserLogin(Resource):

    @staticmethod
    def post():
        data = _parser.parse_args()

        user = UserModel.find_by_username(data['username'])

        if user and compare_digest(user.password, data['password']):
            # access_token = create_access_token(identity=user.username, fresh=True)
            access_token = create_access_token(identity=user.username, fresh=timedelta(minutes=data['expire']))
            refresh_token = create_refresh_token(user.username)
            return {
                       # 'access_token': access_token.decode('utf-8'),  # token needs to be JSON serializable
                       # 'refresh_token': refresh_token.decode('utf-8'), # for earlier versions of pyjwt
                       'access_token': access_token,
                       'refresh_token': refresh_token,
                       'expire': data['expire']
                   }, 200

        return {"message": "Invalid Credentials!"}, 401


class UserLogout(Resource):
    @staticmethod
    @jwt_required()
    def post():
        jti = get_jwt()['jti']  # jti is a unique identifier for JWT
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


class TokenRefresh(Resource):

    @staticmethod
    @jwt_required(refresh=True)
    def post():
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)  # Create not fresh Token if fresh=False
        refresh_token = create_refresh_token(current_user)

        return {
                   'access_token': new_token,
                   'refresh_token': refresh_token
               }, 200
