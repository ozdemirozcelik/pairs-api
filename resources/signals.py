from flask_restful import Resource, reqparse
from models.signals import SignalModel
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from datetime import datetime

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
    parser.add_argument("stk_ticker1", type=str)
    parser.add_argument("stk_ticker2", type=str)
    parser.add_argument("hedge_param", type=float)
    parser.add_argument("order_id1", type=int)
    parser.add_argument("order_id2", type=int)
    parser.add_argument("stk_price1", type=float)
    parser.add_argument("stk_price2", type=float)
    parser.add_argument("fill_price", type=float)
    parser.add_argument("slip", type=float)
    parser.add_argument("error_msg", type=str)

    @staticmethod
    def post():
        data = SignalWebhook.parser.parse_args()

        # format return message inline with flask_restful parser errors
        if SignalModel.passphrase_wrong(data["passphrase"]):
            return_msg = {"message": {"passphrase": PASS_ERR}}
            #  return {"message": PASS_ERR}, 400  # Old return Bad Request
            return return_msg, 400  # Old return Bad Request

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
            data["stk_ticker1"],
            data["stk_ticker2"],
            data["hedge_param"],
            data["order_id1"],
            data["order_id2"],
            data["stk_price1"],
            data["stk_price2"],
            data["fill_price"],
            data["slip"],
            data["error_msg"],
        )

        try:
            ticker_ok = item.splitticker()  # check webhook ticker validity

            active_ok = item.check_ticker_status()

            item.insert()

            if not ticker_ok:
                # keep the ticker record in the database, but change the message
                # do not return bad request
                return {"message": TICKER_ERR}, 201  # Created but need attention

            if not active_ok:
                # keep the ticker record in the database, but change the message
                # do not return bad request
                return {"message": ACTIVE_ERR}, 201  # Created but need attention

        except Exception as e:
            print("Error occurred - ", e)  # better log the errors
            return (
                {"message": INSERT_ERR},
                500,
            )  # Return Interval Server Error

        return (
            {"message": CREATE_OK.format("signal")},
            201,
        )  # Return Successful Creation of Resource

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def put():
        data = SignalWebhook.parser.parse_args()

        # format return message inline with flask_restful parser errors
        if SignalModel.passphrase_wrong(data["passphrase"]):
            return_msg = {"message": {"passphrase": PASS_ERR}}
            #  return {"message": PASS_ERR}, 400  # Old return Bad Request
            return return_msg, 400  # Old return Bad Request

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
                data["stk_ticker1"],
                data["stk_ticker2"],
                data["hedge_param"],
                data["order_id1"],
                data["order_id2"],
                data["stk_price1"],
                data["stk_price2"],
                data["fill_price"],
                data["slip"],
                data["error_msg"],
            )

            try:
                item.splitticker()  # check webhook ticker validity

                item.check_ticker_status()

                item.update(data["rowid"])

            except Exception as e:
                print("Error occurred - ", e)
                return (
                    {"message": UPDATE_ERR},
                    500,
                )  # Return Interval Server Error

            item.rowid = data["rowid"]
            return_json = item.json()

            return_json.pop("timestamp")

            return return_json

        return {"message": NOT_FOUND}, 404  # Return Not Found


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
                500,
            )  # Return Interval Server Error

        # return {'signals': list(map(lambda x: x.json(), items))}  # we can map the list of objects,
        return {
            "signals": [item.json() for item in items],
            "notoken_limit": notoken_limit,
        }  # this is more readable


class SignalListTicker(Resource):
    @staticmethod
    @jwt_required(fresh=True)
    def get(ticker_name, number_of_items="0"):

        try:
            items = SignalModel.get_list_ticker(ticker_name, str(number_of_items))

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": GET_ERR},
                500,
            )  # Return Interval Server Error

        # return {'signals': list(map(lambda x: x.json(), items))}  # we can map the list of objects,
        return {
            "signals": [item.json() for item in items],
        }  # this is more readable


class SignalListStatus(Resource):
    @staticmethod
    @jwt_required(fresh=True)
    def get(order_status, number_of_items="0"):

        try:
            items = SignalModel.get_list_status(order_status, str(number_of_items))

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": GET_ERR},
                500,
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
                500,
            )  # Return Interval Server Error

        if item:
            return item.json()

        return {"message": NOT_FOUND}, 404  # Return Not Found

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def delete(rowid):

        claims = get_jwt()

        # TODO: consider user to delete own data
        if not claims["is_admin"]:
            return {"message": PRIV_ERR.format("admin")}, 401  # Return Unauthorized

        try:
            item_to_delete = SignalModel.find_by_rowid(rowid)

            if item_to_delete:
                item_to_delete.delete()
            else:
                return {"message": NOT_FOUND}

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": DELETE_ERR},
                500,
            )  # Return Interval Server Error

        return {"message": DELETE_OK.format("signal")}
