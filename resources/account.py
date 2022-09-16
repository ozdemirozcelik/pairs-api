from flask_restful import Resource, reqparse
from models.account import AccountModel
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
PART_ERR = "missing contract amount to update partial fill"


class PNLRegister(Resource):
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
    parser.add_argument("AvailableFunds", type=float)
    parser.add_argument("BuyingPower", type=float)
    parser.add_argument("DailyPnL", type=float)
    parser.add_argument("GrossPositionValue", type=float)
    parser.add_argument("MaintMarginReq", type=float)
    parser.add_argument("NetLiquidation", type=float)
    parser.add_argument("RealizedPnL", type=float)
    parser.add_argument("UnrealizedPnL", type=float)

    @staticmethod
    def post():
        data = PNLRegister.parser.parse_args()

        # format return message inline with flask_restful parser errors
        if SignalModel.passphrase_wrong(data["passphrase"]):
            return_msg = {"message": {"passphrase": PASS_ERR}}
            #  return {"message": PASS_ERR}, 400  # return Bad Request
            return return_msg, 400  # return Bad Request

        item = AccountModel(
            data["timestamp"],
            data["AvailableFunds"],
            data["BuyingPower"],
            data["DailyPnL"],
            data["GrossPositionValue"],
            data["MaintMarginReq"],
            data["NetLiquidation"],
            data["RealizedPnL"],
            data["UnrealizedPnL"],
        )

        try:
            item.insert()

        except Exception as e:
            print("Error occurred - ", e)  # better log the errors
            return (
                {"message": INSERT_ERR},
                500,
            )  # Return Interval Server Error

        return (
            {"message": CREATE_OK.format("record")},
            201,
        )  # Return Successful Creation of Resource

    @staticmethod
    def put():
        data = PNLRegister.parser.parse_args()

        # format return message inline with flask_restful parser errors
        if SignalModel.passphrase_wrong(data["passphrase"]):
            return_msg = {"message": {"passphrase": PASS_ERR}}
            #  return {"message": PASS_ERR}, 400  # return Bad Request
            return return_msg, 400  # return Bad Request

        if AccountModel.find_by_rowid(data["rowid"]):

            item = AccountModel(
                data["timestamp"],
                data["AvailableFunds"],
                data["BuyingPower"],
                data["DailyPnL"],
                data["GrossPositionValue"],
                data["MaintMarginReq"],
                data["NetLiquidation"],
                data["RealizedPnL"],
                data["UnrealizedPnL"],
            )

            try:
                item.update(data["rowid"])

            except Exception as e:
                print("Error occurred - ", e)
                return (
                    {"message": UPDATE_ERR},
                    500,
                )  # Return Interval Server Error

            item.rowid = data["rowid"]
            return_json = item.json()

            return return_json

        return {"message": NOT_FOUND}, 404  # Return Not Found


class PNLList(Resource):
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
            items = AccountModel.get_rows(str(number_of_items))

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


class PNL(Resource):
    @staticmethod
    def get(rowid):

        try:
            item = AccountModel.find_by_rowid(rowid)

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
            item_to_delete = AccountModel.find_by_rowid(rowid)

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

    # TODO: add a get(date) function
