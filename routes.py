"""
Resource Definitions for API
"""
from app import app
from flask_restful import Api
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
from resources.account import PNLRegister, PNLList, PNL


api = Api(app)


api.add_resource(SignalWebhook, "/v4/webhook")
api.add_resource(SignalUpdateOrder, "/v4/signal/order")
api.add_resource(SignalList, "/v4/signals/<string:number_of_items>")
api.add_resource(
    SignalListStatus,
    "/v4/signals/status/<string:order_status>/<string:number_of_items>",
)
api.add_resource(
    SignalListTicker, "/v4/signals/ticker/<string:ticker_name>/<string:number_of_items>"
)
api.add_resource(Signal, "/v4/signal/<string:rowid>")

api.add_resource(PairRegister, "/v4/pair")
api.add_resource(PairList, "/v4/pairs/<string:number_of_items>")
api.add_resource(Pair, "/v4/pair/<string:name>")

api.add_resource(TickerRegister, "/v4/ticker")
api.add_resource(TickerUpdatePNL, "/v4/ticker/pnl")
api.add_resource(TickerList, "/v4/tickers/<string:number_of_items>")
api.add_resource(Ticker, "/v4/ticker/<string:symbol>")

api.add_resource(UserRegister, "/v4/user")
api.add_resource(UserList, "/v4/users/<string:number_of_users>")
api.add_resource(User, "/v4/user/<string:username>")
api.add_resource(UserLogin, "/v4/login")
api.add_resource(UserLogout, "/v4/logout")
api.add_resource(TokenRefresh, "/v4/refresh")

api.add_resource(PNLRegister, "/v4/pnl")
api.add_resource(PNLList, "/v4/pnls/<string:number_of_items>")
api.add_resource(PNL, "/v4/pnl/<string:rowid>")
