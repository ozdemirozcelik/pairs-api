from flask_restful import Resource, reqparse
from models.signals import SignalModel
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from datetime import datetime
import math
from . import status_codes as status

EMPTY_ERR = "'{}' cannot be empty!"
PASS_ERR = "incorrect passphrase."
DATE_ERR = "date format should be %Y-%m-%d %H:%M:%S."
TICKER_ERR = "recorded with problematic ticker!"
ACTIVE_ERR = "recorded with unknown or passive ticker!"
INSERT_ERR = "an error occurred inserting the item."
UPDATE_ERR = "an error occurred updating the item."
DELETE_ERR = "an error occurred deleting the item."
GET_ERR = "an error occurred while getting the item(s)."
CREATE_OK = "'{}' created successfully."
DELETE_OK = "'{}' deleted successfully."
NOT_FOUND = "item not found."
PRIV_ERR = "'{}' privilege required."
PART_ERR = "missing contract amount to update partial fill"


class SignalUpdateOrder(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "passphrase", type=str, required=True, help=EMPTY_ERR.format("passphrase")
    )
    parser.add_argument(
        "order_id", type=int, required=True,
    )
    parser.add_argument("symbol", type=str, required=True)
    parser.add_argument("price", type=float, required=True)
    parser.add_argument("filled_qty", type=float, required=True)

    parser.add_argument("cancel", type=bool, default=False)

    # TODO: may not be necessary, check and delete if so
    parser.add_argument("partial", type=bool, default=False)
    parser.add_argument("order_contracts", type=int)

    @staticmethod
    def put():
        data = SignalUpdateOrder.parser.parse_args()

        # format return message inline with flask_restful parser errors
        if SignalModel.passphrase_wrong(data["passphrase"]):
            return_msg = {"message": {"passphrase": PASS_ERR}}
            return return_msg, status.HTTP_401_UNAUTHORIZED  # Unauthorized

        # get signal with rowid
        item = SignalModel.find_by_orderid_ticker(data["order_id"], data["symbol"])

        if item:
            # cancel the order
            if data["cancel"]:
                item.order_status = "canceled"
                item.status_msg = "multiple active orders"

            # TODO: may not be necessary, check and delete if so
            # if updating orders contracts (used for canceled but partially filled orders)
            # assumes that the partially filled order keeps the hedge ratio
            elif data["partial"]:
                if data["order_contracts"]:
                    order_contracts_old = item.order_contracts
                    item.order_contracts = data["order_contracts"]
                    item.order_status = "part.filled"
                    item.status_msg = "canceled amount: " + str(
                        order_contracts_old - item.order_contracts
                    )
                else:
                    return (
                        {"message": PART_ERR},
                        status.HTTP_400_BAD_REQUEST,
                    )  # return Bad Request

            else:
                if item.order_status != "filled":
                    if (
                        item.order_id1 == data["order_id"]
                        and item.ticker1 == data["symbol"]
                    ):  # double check ticker symbol
                        item.price1 = data["price"]
                        item.order_status = "filled(...)"
                        item.status_msg = (
                            "remained("
                            + str(item.ticker1)
                            + str("): ")
                            + str(math.floor(item.order_contracts) - data["filled_qty"])
                        )

                    if (
                        item.order_id2 == data["order_id"]
                        and item.ticker2 == data["symbol"]
                    ):
                        item.price2 = data["price"]
                        item.order_status = "filled(...)"

                    if item.ticker_type == "pair":

                        # if both orders are filled for pairs
                        if item.price1 and item.price2:
                            item.fill_price = round(
                                item.price1 - item.hedge_param * item.price2, 4
                            )

                            if (
                                math.floor(item.order_contracts * item.hedge_param)
                                > data["filled_qty"]
                            ):
                                item.order_status = "part.filled"
                                item.status_msg = (
                                    "remained("
                                    + str(item.ticker2)
                                    + str("): ")
                                    + str(
                                        math.floor(
                                            item.order_contracts * item.hedge_param
                                        )
                                        - data["filled_qty"]
                                    )
                                )
                            else:
                                item.order_status = "filled"
                                item.status_msg = ""

                            # calculate slip if order price is defined,
                            # use 'is not None' to avoid "0" order price problem
                            if item.order_price is not None:
                                if item.order_action == "buy":
                                    item.slip = round(
                                        item.order_price - item.fill_price, 4
                                    )
                                else:
                                    item.slip = -round(
                                        item.order_price - item.fill_price, 4
                                    )

                    else:
                        if item.price1:
                            item.fill_price = item.price1

                            if item.order_contracts > data["filled_qty"]:
                                item.order_status = "part.filled"
                                item.status_msg = "remained: " + str(
                                    item.order_contracts - data["filled_qty"]
                                )
                            else:
                                item.order_status = "filled"
                                item.status_msg = ""

                            # calculate slip if order price is defined
                            if item.order_price is not None:
                                if item.order_action == "buy":
                                    item.slip = round(
                                        item.order_price - item.fill_price, 4
                                    )
                                else:
                                    item.slip = -round(
                                        item.order_price - item.fill_price, 4
                                    )

            try:
                item.update(item.rowid)

            except Exception as e:
                print("Error occurred - ", e)
                return (
                    {"message": UPDATE_ERR},
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                )  # Return Interval Server Error

            return_json = item.json()

            return_json.pop("timestamp")

            return return_json

        return {"message": NOT_FOUND}, status.HTTP_404_NOT_FOUND  # Return Not Found


class SignalWebhook(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "passphrase", type=str, required=True, help=EMPTY_ERR.format("passphrase")
    )
    parser.add_argument("rowid", type=int, default=0)
    parser.add_argument(
        "timestamp",
        type=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
        help=DATE_ERR,
    )
    # parser.add_argument("timestamp", type=str)
    parser.add_argument(
        "ticker", type=str, required=True, help=EMPTY_ERR.format("ticker")
    )
    parser.add_argument(
        "order_action", type=str, required=True, help=EMPTY_ERR.format("order_action"),
    )
    parser.add_argument(
        "order_contracts",
        type=int,
        required=True,
        help=EMPTY_ERR.format("order_contracts"),
    )
    parser.add_argument(
        "order_price", type=float,
    )
    parser.add_argument(
        "mar_pos", type=str,
    )
    parser.add_argument(
        "mar_pos_size", type=int,
    )
    parser.add_argument(
        "pre_mar_pos", type=str,
    )
    parser.add_argument(
        "pre_mar_pos_size", type=int,
    )
    parser.add_argument("order_comment", type=str, default="")
    parser.add_argument("order_status", type=str, default="waiting")
    parser.add_argument("ticker_type", type=str)
    parser.add_argument("ticker1", type=str)
    parser.add_argument("ticker2", type=str)
    parser.add_argument("hedge_param", type=float)
    parser.add_argument("order_id1", type=int)
    parser.add_argument("order_id2", type=int)
    parser.add_argument("price1", type=float)
    parser.add_argument("price2", type=float)
    parser.add_argument("fill_price", type=float)
    parser.add_argument("slip", type=float)
    parser.add_argument("error_msg", type=str)
    parser.add_argument("status_msg", type=str)

    # if you need to bypass active ticker status check
    parser.add_argument("bypass_ticker_status", type=bool, default=False)

    @staticmethod
    def post():
        data = SignalWebhook.parser.parse_args()

        # format return message inline with flask_restful parser errors
        if SignalModel.passphrase_wrong(data["passphrase"]):
            return_msg = {"message": PASS_ERR}
            return return_msg, status.HTTP_401_UNAUTHORIZED  # Return Unauthorized

        item = SignalModel(
            data["timestamp"],
            data["ticker"],
            data["order_action"],
            data["order_contracts"],
            data["order_price"],
            data["mar_pos"],
            data["mar_pos_size"],
            data["pre_mar_pos"],
            data["pre_mar_pos_size"],
            data["order_comment"],
            data["order_status"],
            data["ticker_type"],
            data["ticker1"],
            data["ticker2"],
            data["hedge_param"],
            data["order_id1"],
            data["order_id2"],
            data["price1"],
            data["price2"],
            data["fill_price"],
            data["slip"],
            data["error_msg"],
            data["status_msg"],
        )

        try:
            ticker_ok = item.splitticker()  # check webhook ticker validity

            # if you need to bypass active ticker status check
            if data["bypass_ticker_status"]:
                active_ok = True
            else:
                active_ok = item.check_ticker_status()

            item.insert()

            if not ticker_ok:
                # keep the ticker record in the database, but change the message
                # do not return bad request
                return (
                    {"message": TICKER_ERR},
                    status.HTTP_201_CREATED,
                )  # Created but need attention

            if not active_ok:
                # keep the ticker record in the database, but change the message
                # do not return bad request
                return (
                    {"message": ACTIVE_ERR},
                    status.HTTP_201_CREATED,
                )  # Created but need attention

        except Exception as e:
            print("Error occurred - ", e)  # better log the errors
            return (
                {"message": INSERT_ERR},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )  # Return Interval Server Error

        return (
            {"message": CREATE_OK.format("signal")},
            200,
        )  # Return Successful Creation of Resource

    @staticmethod
    def put():
        data = SignalWebhook.parser.parse_args()

        # format return message inline with flask_restful parser errors
        if SignalModel.passphrase_wrong(data["passphrase"]):
            return_msg = {"message": {"passphrase": PASS_ERR}}
            return return_msg, status.HTTP_401_UNAUTHORIZED  # Return Unauthorized

        if SignalModel.find_by_rowid(data["rowid"]):

            item = SignalModel(
                data["timestamp"],
                data["ticker"],
                data["order_action"],
                data["order_contracts"],
                data["order_price"],
                data["mar_pos"],
                data["mar_pos_size"],
                data["pre_mar_pos"],
                data["pre_mar_pos_size"],
                data["order_comment"],
                data["order_status"],
                data["ticker_type"],
                data["ticker1"],
                data["ticker2"],
                data["hedge_param"],
                data["order_id1"],
                data["order_id2"],
                data["price1"],
                data["price2"],
                data["fill_price"],
                data["slip"],
                data["error_msg"],
                data["status_msg"],
            )

            try:
                item.splitticker()  # check webhook ticker validity

                # if you need to bypass active ticker status check
                if not data["bypass_ticker_status"]:
                    item.check_ticker_status()

                item.update(data["rowid"])

            except Exception as e:
                print("Error occurred - ", e)
                return (
                    {"message": UPDATE_ERR},
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                )  # Return Interval Server Error

            item.rowid = data["rowid"]
            return_json = item.json()

            return_json.pop("timestamp")

            return return_json

        return {"message": NOT_FOUND}, status.HTTP_404_NOT_FOUND  # Return Not Found


class SignalList(Resource):
    @staticmethod
    @jwt_required(optional=True)
    def get(number_of_items="0"):

        username = get_jwt_identity()

        # limit the number of items to get if not logged-in
        notoken_limit = 5

        # without Authorization header, returns None.
        # with Authorization header, returns username
        if username is None:
            if number_of_items == "0":
                number_of_items = max(int(number_of_items), notoken_limit)
            else:
                number_of_items = min(int(number_of_items), notoken_limit)
        try:
            items = SignalModel.get_rows(str(number_of_items))

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": GET_ERR},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )  # Return Interval Server Error

        # return {'signals': list(map(lambda x: x.json(), items))}  # we can map the list of objects,
        return {
            "signals": [item.json() for item in items],
            "notoken_limit": notoken_limit,
        }  # this is more readable


class SignalListTicker(Resource):
    @staticmethod
    @jwt_required(optional=True)
    def get(ticker_name, number_of_items="0"):

        username = get_jwt_identity()

        # limit the number of items to get if not logged-in
        notoken_limit = 5

        # without Authorization header, returns None.
        # with Authorization header, returns username
        if username is None:
            if number_of_items == "0":
                number_of_items = max(int(number_of_items), notoken_limit)
            else:
                number_of_items = min(int(number_of_items), notoken_limit)
        try:
            items = SignalModel.get_list_ticker(ticker_name, str(number_of_items))

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": GET_ERR},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )  # Return Interval Server Error

        # return {'signals': list(map(lambda x: x.json(), items))}  # we can map the list of objects,
        return {
            "signals": [item.json() for item in items],
        }  # this is more readable


class SignalListStatus(Resource):
    @staticmethod
    @jwt_required(optional=True)
    def get(order_status, number_of_items="0"):

        username = get_jwt_identity()

        # limit the number of items to get if not logged-in
        if order_status == "waiting":
            notoken_limit = 20
        else:
            notoken_limit = 5

        # without Authorization header, returns None.
        # with Authorization header, returns username
        if username is None:
            if number_of_items == "0":
                number_of_items = max(int(number_of_items), notoken_limit)
            else:
                number_of_items = min(int(number_of_items), notoken_limit)
        try:
            items = SignalModel.get_list_status(order_status, str(number_of_items))

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": GET_ERR},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )  # Return Interval Server Error

        # return {'signals': list(map(lambda x: x.json(), items))}  # we can map the list of objects,
        return {
            "signals": [item.json() for item in items],
        }  # this is more readable


class Signal(Resource):
    @staticmethod
    def get(rowid):

        try:
            item = SignalModel.find_by_rowid(rowid)

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": GET_ERR},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )  # Return Interval Server Error

        if item:
            return item.json()

        return {"message": NOT_FOUND}, status.HTTP_404_NOT_FOUND  # Return Not Found

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def delete(rowid):

        claims = get_jwt()

        # TODO: consider user to delete own data
        if not claims["is_admin"]:
            return (
                {"message": PRIV_ERR.format("admin")},
                status.HTTP_401_UNAUTHORIZED,
            )  # Return Unauthorized

        try:
            item_to_delete = SignalModel.find_by_rowid(rowid)

            if item_to_delete:
                item_to_delete.delete()
            else:
                return {"message": NOT_FOUND}, status.HTTP_404_NOT_FOUND  # Not Found

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": DELETE_ERR},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )  # Return Interval Server Error

        return {"message": DELETE_OK.format("signal")}
