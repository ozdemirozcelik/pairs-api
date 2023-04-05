"""
This module applies the security policy to the API and the frontend demo
"""

# SeaSurf is preventing cross-site request forgery (CSRF)
# Talisman handles setting HTTP headers to protect against common security issues
# flask_cors handles Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible
from flask_seasurf import SeaSurf
from flask_talisman import Talisman
from flask_cors import CORS
from app import app

# define a content security policy for the script, styles & font sources used for the demo
SELF = "'self'"
csp = {
    "default-src": SELF,
    "img-src": "*",
    "script-src": [SELF, "ajax.googleapis.com"],
    "style-src": [SELF,],
    "font-src": [SELF,],
}

nonce_list = ["default-src", "script-src"]

csrf = SeaSurf(app)

# add csrf exception routes.
# these routes are to be reached from external sources with a passphrase
csrf._exempt_urls = (
    "/v4/webhook",
    "/v4/signal/order",
    "/v4/ticker/pnl",
)

talisman = Talisman(
    app, content_security_policy=csp, content_security_policy_nonce_in=nonce_list
)
CORS(app)
