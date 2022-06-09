from flask_restful import Resource, reqparse
from models.stocks import StockModel
from flask_jwt_extended import jwt_required, get_jwt
from models.pairs import PairModel

EMPTY_ERR = "'{}' cannot be empty!"
NAME_ERR = "'{}' with that name already exists."
INSERT_ERR = "an error occurred inserting the item."
UPDATE_ERR = "an error occurred updating the item."
DELETE_ERR = "an error occurred deleting the item."
GET_ERR = "an error occurred while getting the item(s)."
CREATE_OK = "'{}' created successfully."
DELETE_OK = "'{}' deleted successfully."
NOT_FOUND = "item not found."
PRIV_ERR = "'{}' privilege required."
TICKR_ERR = " stock is already active in a pair!"


class StockRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "symbol", type=str, required=True, help=EMPTY_ERR.format("symbol")
    )
    parser.add_argument("prixch", type=str, default="SMART")
    parser.add_argument("secxch", type=str, default="ISLAND")
    parser.add_argument("active", type=int, default=0)

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def post():
        data = StockRegister.parser.parse_args()

        if StockModel.find_by_symbol(data["symbol"]):
            return (
                {"message": NAME_ERR.format("stock")},
                400,
            )  # Return Bad Request

        item = StockModel(
            data["symbol"], data["prixch"], data["secxch"], data["active"]
        )
        
        if item.active == 1:

            if PairModel.find_active_ticker(item.symbol):
                return (
                    {"message": TICKR_ERR},
                    400,
                )  # Return Bad Request

        try:
            item.insert()

        except Exception as e:
            print("Error occurred - ", e)  # better log the errors
            return (
                {"message": INSERT_ERR},
                500,
            )  # Return Interval Server Error

        return (
            {"message": CREATE_OK.format("stock")},
            201,
        )  # Return Successful Creation of Resource

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def put():
        data = StockRegister.parser.parse_args()

        item = StockModel(
            data["symbol"], data["prixch"], data["secxch"], data["active"]
        )

        if item.active == 1:

            if PairModel.find_active_ticker(item.symbol):
                return (
                    {"message": TICKR_ERR},
                    400,
                )  # Return Bad Request

        if StockModel.find_by_symbol(data["symbol"]):
            try:
                item.update()

            except Exception as e:
                print("Error occurred - ", e)
                return (
                    {"message": UPDATE_ERR},
                    500,
                )  # Return Interval Server Error

            return item.json()

        try:
            item.insert()

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": INSERT_ERR},
                500,
            )  # Return Interval Server Error

        return (
            {"message": CREATE_OK.format("stock")},
            201,
        )  # Return Successful Creation of Resource


class StockList(Resource):
    @staticmethod
    def get(number_of_items="0"):
        try:
            items = StockModel.get_rows(number_of_items)

        except Exception as e:
            print("Error occurred - ", e)
            return (
                {"message": GET_ERR},
                500,
            )  # Return Interval Server Error

        # return {'stocks': list(map(lambda x: x.json(), items))}  # we can map the list of objects,
        return {
            "stocks": [item.json() for item in items]
        }  # but this one is slightly more readable


class Stock(Resource):
    @staticmethod
    def get(symbol):

        try:
            item = StockModel.find_by_symbol(symbol)

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
    def delete(symbol):

        claims = get_jwt()

        # TODO: consider user to delete own data
        if not claims["is_admin"]:
            return {"message": PRIV_ERR.format("admin")}, 401  # Return Unauthorized

        try:
            item_to_delete = StockModel.find_by_symbol(symbol)

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

        return {"message": DELETE_OK.format("stock")}
