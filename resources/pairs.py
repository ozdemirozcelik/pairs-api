from flask_restful import Resource, reqparse
from models.pairs import PairModel
from flask_jwt_extended import jwt_required, get_jwt
from models.tickers import TickerModel

EMPTY_ERR = "'{}' cannot be empty!"
NAME_ERR = "'{}' with that name already exists."
TICKER_ERR = "problematic ticker!"
INSERT_ERR = "an error occurred inserting the item."
UPDATE_ERR = "an error occurred updating the item."
DELETE_ERR = "an error occurred deleting the item."
GET_ERR = "an error occurred while getting the item(s)."
CREATE_OK = "'{}' created successfully."
DELETE_OK = "'{}' deleted successfully."
NOT_FOUND = "item not found."
PRIV_ERR = "'{}' privilege required."
STK_ERR = " one of the tickers is already active!"


class PairRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str)
    parser.add_argument(
        "ticker1", type=str, required=True, help=EMPTY_ERR.format("ticker1")
    )
    parser.add_argument(
        "ticker2", type=str, required=True, help=EMPTY_ERR.format("ticker2")
    )
    parser.add_argument(
        "hedge", type=float, required=True, help=EMPTY_ERR.format("hedge")
    )
    parser.add_argument(
        "status", type=int, default=0,
    )
    parser.add_argument("notes", type=str)

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def post():
        data = PairRegister.parser.parse_args()

        item = PairModel(
            data["name"],
            data["ticker1"],
            data["ticker2"],
            data["hedge"],
            data["status"],
            data["notes"],
        )

        if item.status == 1:

            if TickerModel.find_active_ticker(item.ticker1, item.ticker2):
                return (
                    {"message": STK_ERR},
                    400,
                )  # Return Bad Request

        try:
            ticker_ok = item.combineticker()  # combine tickers & create pair name

            if ticker_ok:

                if PairModel.find_by_name(item.name):
                    return (
                        {"message": NAME_ERR.format("pair")},
                        400,
                    )  # Return Bad Request

                item.insert()
            else:
                return (
                    {"message": TICKER_ERR},
                    400,
                )  # Return Bad Request

        except Exception as e:
            print("Error occurred - ", e)  # better log the errors
            return (
                {"message": INSERT_ERR},
                500,
            )  # Return Interval Server Error

        return (
            {"message": CREATE_OK.format("pair")},
            201,
        )  # Return Successful Creation of Resource

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def put():
        data = PairRegister.parser.parse_args()

        item = PairModel(
            data["name"],
            data["ticker1"],
            data["ticker2"],
            data["hedge"],
            data["status"],
            data["notes"],
        )

        if item.status == 1:

            if TickerModel.find_active_ticker(item.ticker1, item.ticker2):
                return (
                    {"message": STK_ERR},
                    400,
                )  # Return Bad Request

        item_to_return = PairModel.find_by_name(data["name"])

        if item_to_return:
            try:
                item.update()

            except Exception as e:
                print("Error occurred - ", e)
                return (
                    {"message": UPDATE_ERR},
                    500,
                )  # Return Interval Server Error

            return item_to_return.json()

        return {"message": NOT_FOUND}, 404  # Return Not Found


class PairList(Resource):
    @staticmethod
    def get(number_of_items="0"):
        try:
            items = PairModel.get_rows(number_of_items)

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": GET_ERR},
                500,
            )  # Return Interval Server Error

        # return {'pairs': list(map(lambda x: x.json(), items))}  # we can map the list of objects,
        return {
            "pairs": [item.json() for item in items]
        }  # but this one is slightly more readable


class Pair(Resource):
    @staticmethod
    def get(name):

        try:
            item = PairModel.find_by_name(name)

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": GET_ERR},
                500,
            )  # Return Interval Server Error

        if item:
            return item.json()

        return {"message": "Item not found"}, 404  # Return Not Found

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def delete(name):

        claims = get_jwt()

        # TODO: consider user to delete own data
        if not claims["is_admin"]:
            return {"message": PRIV_ERR.format("admin")}, 401  # Return Unauthorized

        try:
            item_to_delete = PairModel.find_by_name(name)

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

        return {"message": DELETE_OK.format("pair")}
