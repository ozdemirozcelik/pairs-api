"""
Global Configuration
"""

import os
from app import app
from flask_jwt_extended import JWTManager


### DATABASE CONFIGURATION ###

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


### JWT CONFIGURATION ###
app.config["JWT_SECRET_KEY"] = os.urandom(24)
app.config["JWT_BLACKLIST_ENABLED"] = True  # enable blacklist feature
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = [
    "access",
    "refresh",
]  # allow blacklisting for access and refresh tokens

jwt = JWTManager(app)


### SESSION CONFIGURATION ###

app.secret_key = os.urandom(24)  # need this for session management

# (flask-session-change) Enable below to keep session data with SQLAlchemy:
# sessions work ok locally but may not be persistent with Heroku free tier.

# from flask_session import Session
# from flask import session

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

# # Enable if using sessions with SQLAlchemy to create table to store session data:
# #
# Fsession = Session(app)
#
# with app.app_context():
#     if app.config["SESSION_TYPE"] == "sqlalchemy":
#         Fsession.app.session_interface.db.create_all()
# #
