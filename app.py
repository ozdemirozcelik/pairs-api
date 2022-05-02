from flask import Flask, render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager
from jwt import ExpiredSignatureError
from blacklist import BLACKLIST
from resources.pairs import PairRegister, PairList, Pair
from resources.signals import SignalWebhook, SignalList, Signal
from resources.stocks import StockRegister, StockList, Stock
from resources.users import UserRegister, UserList, User, UserLogin, UserLogout, TokenRefresh
import requests
from db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # database location
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # flask-sqlalchemy tracker is off, sqlalchemy has its own tracker
app.config['PROPAGATE_EXCEPTIONS'] = True  # to allow flask propagating exception even if debug is set to false


# Create tables and default users
@app.before_first_request
def create_tables():
    db.create_all()
    UserRegister.default_users()


db.init_app(app)

if __name__ == '__main__':  # to avoid duplicate calls
    app.run(debug=True)

api = Api(app)

# JWT configuration (Start)

app.config['JWT_SECRET_KEY'] = 'mysecretkey'  # TODO: check the use of this
app.config['JWT_BLACKLIST_ENABLED'] = True  # enable blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # allow blacklisting for access and refresh tokens
jwt = JWTManager(app)


# If necessary to check admin rights, is_admin can be used
@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == "admin":  # TODO: read from a config file
        return {'is_admin': True}
    return {'is_admin': False}


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in BLACKLIST


@jwt.expired_token_loader
def my_expired_token_callback(*args):
    return {
               'message': 'The token has expired.',
               'error': 'token_expired'
           }, 401


# TODO: Solution to invalid token returns 500 instead of 401
# jwt.exceptions.ExpiredSignatureError: Signature has expired
# check the workaround: _handle_expired_signature
@jwt.invalid_token_loader
def my_invalid_token_callback(*args):
    return {
               'message': 'The token is invalid.',
               'error': 'token_invalid'
           }, 401


@app.errorhandler(ExpiredSignatureError)
def _handle_expired_signature(error):
    return {
               'message': 'The token is invalid.',
               'error': 'token_invalid'
           }, 401


@jwt.unauthorized_loader
def my_missing_token_callback(error):
    return {
               "message": "Request does not contain an access token.",
               'error': 'authorization_required'
           }, 401


@jwt.needs_fresh_token_loader
def my_token_not_fresh_callback(jwt_header, jwt_payload):
    return {
               "message": "The token is not fresh.",
               'error': 'fresh_token_required'
           }, 401


@jwt.revoked_token_loader
def my_revoked_token_callback(jwt_header, jwt_payload):
    return {
               "message": "The token has been revoked.",
               'error': 'token_revoked'
           }, 401


# JWT configuration (End)

# Resource definitions (Start)

api.add_resource(SignalWebhook, '/v3/webhook')
api.add_resource(SignalList, '/v3/signals/<string:number_of_items>')
api.add_resource(Signal, '/v3/signal/<string:rowid>')

api.add_resource(PairRegister, '/v3/regpair')
api.add_resource(PairList, '/v3/pairs/<string:number_of_items>')
api.add_resource(Pair, '/v3/pair/<string:name>')

api.add_resource(StockRegister, '/v3/regstock')
api.add_resource(StockList, '/v3/stocks/<string:number_of_items>')
api.add_resource(Stock, '/v3/stock/<string:symbol>')

api.add_resource(UserRegister, '/v3/reguser')
api.add_resource(UserList, '/v3/users/<string:number_of_users>')
api.add_resource(User, '/v3/user/<string:username>')
api.add_resource(UserLogin, '/v3/login')
api.add_resource(UserLogout, '/v3/logout')
api.add_resource(TokenRefresh, '/v3/refresh')

# Resource definitions (End)


# # enable if running locally
# server_url = "http://127.0.0.1:5000/"


# disable if running locally
# test server url:
server_url = "http://api-pairs.herokuapp.com/"

# proxy to bypass CORS limitations
proxies = {
    'get': 'https://api-pairs-cors.herokuapp.com/'
    }


@app.get('/')
def dashboard():
    server_url_read = server_url + "v3/signals/50"  # get the recent 50 signals

    try:
        # # disable if using locally:
        # response = requests.get(server_url_read, proxies=proxies, timeout=10)

        # enable if using locally:
        response = requests.get(server_url_read, timeout=5)

    except requests.Timeout:
        # back off and retry
        print(f'timeout error')
        pass
    except requests.ConnectionError:
        print(f'connection error')
        pass

    signals = response.json()['signals']

    return render_template('dashboard.html', signals=signals)


@app.get('/apitest')
def apitest():
    return render_template('apitest.html')
