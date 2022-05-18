import os
from flask import Flask, render_template, request, session
from flask_restful import Api
from flask_jwt_extended import JWTManager, get_jwt_identity
from jwt import ExpiredSignatureError
from blacklist import BLACKLIST
from models.signals import SignalModel
from resources.pairs import PairRegister, PairList, Pair
from resources.signals import (
    SignalWebhook,
    SignalList,
    SignalListTicker,
    SignalListStatus,
    Signal,
)
from resources.stocks import StockRegister, StockList, Stock
from resources.users import (
    UserRegister,
    UserList,
    User,
    UserLogin,
    UserLogout,
    TokenRefresh,
)
import requests
from db import db
from datetime import datetime
import pytz
from pytz import timezone

app = Flask(__name__)
# check for postgres database, if not found use local sqlite database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL_SQLALCHEMY", "sqlite:///data.db"
)
app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False  # flask-sqlalchemy tracker is off, sqlalchemy has its own tracker
app.config[
    "PROPAGATE_EXCEPTIONS"
] = True  # to allow flask propagating exception even if debug is set to false

if __name__ == "__main__":  # to avoid duplicate calls
    app.run(debug=True)

api = Api(app)

db.init_app(app)


# Create tables and default users
@app.before_first_request
def create_tables():
    db.create_all()
    UserRegister.default_users()


# JWT configuration (Start)

app.secret_key = "super secret key"  # need for session management
app.config["JWT_SECRET_KEY"] = "mysecretkey"  # TODO: check the use of this
app.config["JWT_BLACKLIST_ENABLED"] = True  # enable blacklist feature
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = [
    "access",
    "refresh",
]  # allow blacklisting for access and refresh tokens
jwt = JWTManager(app)


# If necessary to check admin rights, is_admin can be used
@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == "admin":  # TODO: read from a config file
        return {"is_admin": True}
    return {"is_admin": False}


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST


@jwt.expired_token_loader
def my_expired_token_callback(*args):
    return {"message": "The token has expired.", "error": "token_expired"}, 401


# TODO: Solution to invalid token returns 500 instead of 401
# jwt.exceptions.ExpiredSignatureError: Signature has expired
# check the workaround: _handle_expired_signature
@jwt.invalid_token_loader
def my_invalid_token_callback(*args):
    session["token"] = "no_token"
    return {"message": "The token is invalid.", "error": "token_invalid"}, 401


@app.errorhandler(ExpiredSignatureError)
def _handle_expired_signature(error):
    session["token"] = "no_token"
    return {"message": "The token is invalid.", "error": "token_invalid"}, 401


@jwt.unauthorized_loader
def my_missing_token_callback(error):
    return (
        {
            "message": "Request does not contain an access token.",
            "error": "authorization_required",
        },
        401,
    )


@jwt.needs_fresh_token_loader
def my_token_not_fresh_callback(jwt_header, jwt_payload):
    return {"message": "The token is not fresh.", "error": "fresh_token_required"}, 401


@jwt.revoked_token_loader
def my_revoked_token_callback(jwt_header, jwt_payload):
    return {"message": "The token has been revoked.", "error": "token_revoked"}, 401


# JWT configuration (End)

# Resource definitions (Start)

api.add_resource(SignalWebhook, "/v2/webhook")
api.add_resource(SignalList, "/v2/signals/<string:number_of_items>")
api.add_resource(
    SignalListStatus,
    "/v2/signals/status/<string:order_status>/<string:number_of_items>",
)
api.add_resource(
    SignalListTicker, "/v2/signals/ticker/<string:ticker_name>/<string:number_of_items>"
)
api.add_resource(Signal, "/v2/signal/<string:rowid>")

api.add_resource(PairRegister, "/v2/regpair")
api.add_resource(PairList, "/v2/pairs/<string:number_of_items>")
api.add_resource(Pair, "/v2/pair/<string:name>")

api.add_resource(StockRegister, "/v2/regstock")
api.add_resource(StockList, "/v2/stocks/<string:number_of_items>")
api.add_resource(Stock, "/v2/stock/<string:symbol>")

api.add_resource(UserRegister, "/v2/reguser")
api.add_resource(UserList, "/v2/users/<string:number_of_users>")
api.add_resource(User, "/v2/user/<string:username>")
api.add_resource(UserLogin, "/v2/login")
api.add_resource(UserLogout, "/v2/logout")
api.add_resource(TokenRefresh, "/v2/refresh")


# Resource definitions (End)


@app.get("/")
def dashboard():
    # signals = SignalList.get("50")

    if session.get("token") == "yes_token":
        items = SignalModel.get_rows(str(50))
    else:
        items = SignalModel.get_rows(str(5))

    signals = [item.json() for item in items]

    return render_template("dashboard.html", signals=signals)


# test api through url, may not work for some servers (such as Heroku)
@app.get("/dashboard")
def url_dashboard():
    base_url = request.base_url
    server_url_read = base_url + "v2/signals/50"  # get the recent 50 signals

    try:

        response = requests.get(server_url_read, timeout=5)

        # # enable below to bypass CORS limitations
        # proxies = {"get": "https://api-pairs-cors.herokuapp.com/"}
        # response = requests.get(server_url_read, proxies=proxies, timeout=10)

    except requests.Timeout:
        # back off and retry
        print(f"timeout error")
        pass
    except requests.ConnectionError:
        print(f"connection error")
        pass

    return render_template("dashboard.html", signals=response.json()["signals"])


@app.get("/setup")
def apitest():
    return render_template("apitest.html")


# Template filters below:

# check if the date is today's date
@app.template_filter("iftoday")
def iftoday(value):
    date_format = "%Y-%m-%d %H:%M:%S"
    date_signal = datetime.strptime(value, date_format)  # convert string to timestamp

    date_now = datetime.now(tz=pytz.utc)
    date_now_formatted = date_now.strftime(date_format)  # format as string
    date_now_final = datetime.strptime(
        date_now_formatted, date_format
    )  # convert to timestamps

    if date_now_final.day == date_signal.day:
        return True
    else:
        return False


# edit the timezone to display at the dashboard, currently set to UTC
@app.template_filter("pct_time")
def pct_time(value):
    date_format = "%Y-%m-%d %H:%M:%S"
    date_signal = datetime.strptime(value, date_format)  # convert string to timestamp
    date_signal_utc = date_signal.replace(tzinfo=pytz.UTC)  # add tz info
    date_pct = date_signal_utc.astimezone(timezone("US/Pacific"))  # change tz
    date_final = date_pct.strftime(date_format)  # convert to str

    if value is None:
        return ""
    return date_final


# calculate time difference in minutes
@app.template_filter("timediff")
def timediff(value):
    date_format = "%Y-%m-%d %H:%M:%S"
    date_signal = datetime.strptime(value, date_format)  # convert string to timestamp

    date_now = datetime.now(tz=pytz.utc)
    date_now_formatted = date_now.strftime(date_format)  # format as string
    date_now_final = datetime.strptime(
        date_now_formatted, date_format
    )  # convert to timestamp

    date_diff = (date_now_final - date_signal).total_seconds() / 60.0

    if value is None:
        return ""
    return round(date_diff)

