"""
Loaders & Error Handlers
"""

from config import jwt
from app import app
from jwt import ExpiredSignatureError


# Create tables and default users
@app.before_first_request
def create_tables():
    from app import db
    from services.resources.users import UserRegister

    db.create_all()
    UserRegister.default_users()


# If necessary to check admin rights, is_admin can be used
@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    from app import configs

    admin_username = configs.get("SECRET", "ADMIN_USERNAME")
    if identity == admin_username:  # TODO: read from a config file
        return {"is_admin": True}
    return {"is_admin": False}


# This method will check if a token is blacklisted,
# and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    from blacklist import BLACKLIST

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


@app.errorhandler(ExpiredSignatureError)
def _handle_expired_signature(error):
    # (flask-session-change) enable if using sessions to end session:
    # session["token"] = None
    return {"message": "The token is invalid.", "error": "token_invalid"}, 401
