import os
from flask import Flask, render_template, request, flash, redirect, url_for

# (flask-session-change) enable if using flask sessions, currently using custom created session management:
# from flask_session import Session
# from flask import session
from flask_restful import Api
from flask_jwt_extended import JWTManager
from jwt import ExpiredSignatureError
from blacklist import BLACKLIST
from models.signals import SignalModel
from models.tickers import TickerModel
from models.pairs import PairModel
from models.session import SessionModel
from resources.pairs import PairRegister, PairList, Pair
from resources.signals import (
    SignalWebhook,
    SignalUpdateOrder,
    SignalList,
    SignalListTicker,
    SignalListStatus,
    Signal,
)
from resources.tickers import TickerRegister, TickerUpdatePNL, TickerList, Ticker
from resources.users import (
    UserRegister,
    UserList,
    User,
    UserLogin,
    UserLogout,
    TokenRefresh,
)
from db import db
from datetime import datetime
from datetime import timedelta
import pytz
from pytz import timezone

app = Flask(__name__)

# Use below config to use with POSTGRES:
# check for env variable (postgres), if not found use local sqlite database
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


# Session configuration (Start)

app.secret_key = os.urandom(24)  # need this for session management

# (flask-session-change) Enable below to keep session data with SQLAlchemy:
# sessions work ok locally but may not be persistent with Heroku free tier.
# TODO: try to keep session data with Redis

# app.config["SESSION_TYPE"] = "sqlalchemy"
# app.config["SESSION_SQLALCHEMY"] = db  # SQLAlchemy object
# app.config["SESSION_SQLALCHEMY_TABLE"] = "session"  # session table name
# app.config["SESSION_PERMANENT"] = True
# app.config["SESSION_USE_SIGNER"] = False  # browser session cookie value to encrypt
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
# app.config[
#     "SESSION_KEY_PREFIX"
# ] = "session:"  # the prefix of the value stored in session


# (flask-session-change) Enable below to keep session data in the file system:

# app.config["SESSION_TYPE"] = "filesystem"
# app.config["SESSION_PERMANENT"] = True
# app.config["SESSION_USE_SIGNER"] = False  # browser session cookie value to encrypt
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
# app.config[
#     "SESSION_KEY_PREFIX"
# ] = "session:"  # the prefix of the value stored in session

## Enable if using sessions with SQLAlchemy to create table to store session data:
##
# Fsession = Session(app)
#
# with app.app_context():
#     if app.config["SESSION_TYPE"] == "sqlalchemy":
#         Fsession.app.session_interface.db.create_all()
##

# Session configuration (End)

# JWT configuration (Start)
app.config["JWT_SECRET_KEY"] = os.urandom(24)
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


# TODO: Check for another solution to invalid token returns 500 instead of 401
# jwt.exceptions.ExpiredSignatureError: Signature has expired
# check the workaround: _handle_expired_signature
@jwt.invalid_token_loader
def my_invalid_token_callback(*args):
    # (flask-session-change) enable if using sessions to end session:
    # session["token"] = None
    return {"message": "The token is invalid.", "error": "token_invalid"}, 401


@app.errorhandler(ExpiredSignatureError)
def _handle_expired_signature(error):
    # (flask-session-change) enable if using sessions to end session:
    # session["token"] = None
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

api.add_resource(SignalWebhook, "/v3/webhook")
api.add_resource(SignalUpdateOrder, "/v3/signal/updateorder")
api.add_resource(SignalList, "/v3/signals/<string:number_of_items>")
api.add_resource(
    SignalListStatus,
    "/v3/signals/status/<string:order_status>/<string:number_of_items>",
)
api.add_resource(
    SignalListTicker, "/v3/signals/ticker/<string:ticker_name>/<string:number_of_items>"
)
api.add_resource(Signal, "/v3/signal/<string:rowid>")

api.add_resource(PairRegister, "/v3/regpair")
api.add_resource(PairList, "/v3/pairs/<string:number_of_items>")
api.add_resource(Pair, "/v3/pair/<string:name>")

api.add_resource(TickerRegister, "/v3/regticker")
api.add_resource(TickerUpdatePNL, "/v3/ticker/updatepnl")
api.add_resource(TickerList, "/v3/tickers/<string:number_of_items>")
api.add_resource(Ticker, "/v3/ticker/<string:symbol>")

api.add_resource(UserRegister, "/v3/reguser")
api.add_resource(UserList, "/v3/users/<string:number_of_users>")
api.add_resource(User, "/v3/user/<string:username>")
api.add_resource(UserLogin, "/v3/login")
api.add_resource(UserLogout, "/v3/logout")
api.add_resource(TokenRefresh, "/v3/refresh")


# Resource definitions (End)


@app.route("/")
def home():
    return redirect("/dashboard")


@app.get("/dashboard")
def dashboard():
    # (flask-session-change) Flask sessions may not be persistent in Heroku, works fine in local
    # consider disabling below for Heroku

    ##
    # if session.get("token") is None:
    #     session["token"] = None
    #
    # if session["token"] == "yes_token":
    #     items = SignalModel.get_rows(str(50))
    # else:
    #     items = SignalModel.get_rows(str(5))
    #     flash("Login to see more!", "login_for_more")
    #
    # signals = [item.json() for item in items]
    ##

    # consider enabling below for Heroku:
    # this method uses a simple custom session table created in the database

    access_token = request.cookies.get("access_token")

    SessionModel.delete_expired()  # clean expired session data

    if access_token:
        simplesession = SessionModel.find_by_value(access_token[-10:])
    else:
        simplesession = None

    if simplesession:
        items = SignalModel.get_rows(str(20))

    else:
        items = SignalModel.get_rows(str(5))
        flash("Login to see more!", "login_for_more")

    signals = [item.json() for item in items]

    return render_template(
        "dash.html", signals=signals, title="DASHBOARD", tab1="tab active", tab2="tab", tab3="tab"
    )


@app.get("/list")
def dashboard_list():
    # (flask-session-change) Flask sessions may not be persistent in Heroku, works fine in local
    # consider disabling below for Heroku

    ##
    # selected_ticker = request.args.get('ticker_webhook')  # get from the form submission

    # if session.get("token") is None:
    #     session["token"] = None
    #
    # if session["token"] == "yes_token":
    #     items = SignalModel.get_list_ticker(selected_ticker,"0")
    # else:
    #     items = SignalModel.get_list_ticker(selected_ticker,"5")
    #     flash("Login to see more!", "login_for_more")
    #
    # signals = [item.json() for item in items]
    ##

    # consider enabling below for Heroku:
    # this method uses a simple custom session table created in the database

    # get form submission
    selected_ticker = request.args.get("ticker_webhook")
    selected_trade_type = request.args.get("tradetype")
    start_date_selected = request.args.get("start_date")
    end_date_selected = request.args.get("end_date")

    date_format = "%Y-%m-%d"

    try:
        start_date = start_date_selected.split(".")[
            0
        ]  # clean the timezone info if necessary
        start_date = datetime.strptime(
            start_date, date_format
        )  # convert string to timestamp
        end_date = end_date_selected.split(".")[
            0
        ]  # clean the timezone info if necessary
        end_date = datetime.strptime(
            end_date, date_format
        )  # convert string to timestamp
        end_date = end_date + timedelta(
            days=1
        )  # Add 1 day to "%Y-%m-%d" 00:00:00 to reach end of day

    except:
        start_date = datetime.now(tz=pytz.utc) - timedelta(days=1)
        date_now = datetime.now(tz=pytz.utc)
        date_now_formatted = date_now.strftime(date_format)  # format as string
        start_date = datetime.strptime(
            date_now_formatted, date_format
        )  # convert to timestamp
        end_date = start_date + timedelta(days=1)  # Today end of day

    access_token = request.cookies.get("access_token")

    SessionModel.delete_expired()  # clean expired session data

    if access_token:
        simplesession = SessionModel.find_by_value(access_token[-10:])
    else:
        simplesession = None

    if selected_ticker:
        if simplesession:
            items = SignalModel.get_list_ticker_dates(
                selected_ticker, "0", start_date, end_date
            )
        else:
            items = SignalModel.get_list_ticker_dates(
                selected_ticker, "5", start_date, end_date
            )
            flash("Login to see more!", "login_for_more")
    else:
        return render_template(
            "list.html", title="LIST SIGNALS", tab2="tab active", tab1="tab", tab3="tab"
        )

    signals = [item.json() for item in items]

    return render_template(
        "list.html",
        signals=signals,
        title="LIST SIGNALS",
        tab2="tab active",
        tab1="tab",
        tab3="tab",
        start_date=start_date,
        end_date=end_date - timedelta(days=1),
        selected_ticker=selected_ticker,
        selected_trade_type=selected_trade_type,
    )

@app.get("/positions")
def positions():
    # (flask-session-change) Flask sessions may not be persistent in Heroku, works fine in local
    # consider disabling below for Heroku

    ##
    # if session.get("token") is None:
    #     session["token"] = None
    #
    # if session["token"] == "yes_token":
    #     items = SignalModel.get_rows(str(50))
    # else:
    #     items = SignalModel.get_rows(str(5))
    #     flash("Login to see more!", "login_for_more")
    #
    # signals = [item.json() for item in items]
    ##

    # consider enabling below for Heroku:
    # this method uses a simple custom session table created in the database

    access_token = request.cookies.get("access_token")

    SessionModel.delete_expired()  # clean expired session data

    if access_token:
        simplesession = SessionModel.find_by_value(access_token[-10:])
    else:
        simplesession = None

    if simplesession:
        active_tickers = TickerModel.get_active_tickers(str(20))
        active_pairs = PairModel.get_active_pairs(str(20))

    else:
        active_tickers = TickerModel.get_active_tickers(str(3))
        active_pairs = PairModel.get_active_pairs(str(3))
        flash("Login for more details!", "login_for_more")

    pairs = [item.json() for item in active_pairs]
    print(active_pairs)

    pairs_ticker = []

    for item in active_pairs:
        pairs_ticker.append(TickerModel.find_by_symbol(item.ticker1).json())
        pairs_ticker.append(TickerModel.find_by_symbol(item.ticker2).json())

    tickers = [item.json() for item in active_tickers]

    return render_template(
        "pos.html", pairs=pairs, tickers=tickers, pairs_ticker=pairs_ticker, title="POSITIONS", tab3="tab active", tab2="tab", tab1="tab"
    )


# route to setup page
@app.get("/setup")
def setup():
    # (flask-session-change) session may not be persistent in Heroku, works fine in local
    # consider disabling below for Heroku

    ##
    # if session.get("token") is None:
    #     session["token"] = None
    #
    # if session["token"] == "yes_token":
    #     return render_template("setup.html")
    # else:
    #     # show login message and bo back to dashboard
    #     flash("Please login!","login")
    #     return redirect(url_for('dashboard'))
    ##

    # consider enabling below for Heroku:
    # this method does not confirm the session on the server side
    # JWT tokens are still needed for API, so no need to worry

    access_token = request.cookies.get("access_token")

    if access_token:
        return render_template("setup.html")
    else:
        # show login message and bo back to dashboard
        flash("Please login!", "login")
        return redirect(url_for("dashboard"))


# TEMPLATE FILTERS BELOW:

# check if the date is today's date
@app.template_filter("iftoday")
def iftoday(value):
    date_format = "%Y-%m-%d %H:%M:%S"
    value = value.split(".")[0]  # clean the timezone info if necessary
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
    value = value.split(".")[0]  # clean the timezone info if necessary
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
    value = value.split(".")[0]  # clean the timezone info if necessary
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
