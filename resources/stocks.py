from flask_restful import Resource, reqparse
from models.stocks import StockModel

TABLE_STOCKS = 'stocks'


class StocksRegister(Resource):
    parser_stocks = reqparse.RequestParser()

    # parser_stocks.add_argument('stocks', type=dict)
    parser_stocks.add_argument('stocks', type=dict, action='append')


    @staticmethod
    def post():
        data_stocks = StocksRegister.parser_stocks.parse_args()

        nested_parser = reqparse.RequestParser()
        nested_parser.add_argument('symbol', type=str, location=('stocks',))
        nested_args = nested_parser.parse_args(req=data_stocks['stocks'][0])

        # nested_one_parser = reqparse.RequestParser()
        # nested_one_parser.add_argument('symbol', type=str, location=('stocks',))
        # nested_one_args = nested_one_parser.parse_args(req=data_stocks)

        print(data_stocks)
        print("****")
        print(nested_args)

        # if StockModel.find_by_symbol(data_stocks['stocks']['symbol']):
        if StockModel.find_by_symbol(data_stocks['stocks'][0]['symbol']):
            return {"message": "Stock with that name already exists."}, 400  # Return Bad Request

        item = StockModel(data_stocks['symbol'], data_stocks['prixch'], data_stocks['secxch'], data_stocks['active'])

        try:
            item.insert()

        except Exception as e:
            print('Error occurred - ', e)  # better log the errors
            return {"message": "An error occurred inserting the item."}, 500  # Return Interval Server Error

        return {"message": "Stock created successfully."}, 201  # Return Successful Creation of Resource

    @staticmethod
    def put():
        data = StocksRegister.parser.parse_args()
        item = StockModel.find_by_symbol(data['symbol'])

        item_to_put = StockModel(data['symbol'], data['prixch'], data['secxch'], data['active'])

        if item:
            try:
                item_to_put.update()

            except Exception as e:
                print('Error occurred - ', e)
                return {"message": "An error occurred updating the item."}, 500  # Return Interval Server Error

            return item_to_put.json()

        try:
            item_to_put.insert()

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred inserting the item."}, 500  # Return Interval Server Error

        return {"message": "Stock created successfully."}, 201  # Return Successful Creation of Resource


class StockRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('symbol',
                        type=str,
                        required=True,
                        help="Symbol cannot be empty!"
                        )
    parser.add_argument('prixch',
                        type=str,
                        default="SMART"
                        )
    parser.add_argument('secxch',
                        type=str,
                        default="ISLAND"
                        )
    parser.add_argument('active',
                        type=int,
                        default=0
                        )


    @staticmethod
    def post():
        data = StockRegister.parser.parse_args()

        if StockModel.find_by_symbol(data['symbol']):
            return {"message": "Stock with that name already exists."}, 400  # Return Bad Request

        item = StockModel(data['symbol'], data['prixch'], data['secxch'], data['active'])

        try:
            item.insert()

        except Exception as e:
            print('Error occurred - ', e)  # better log the errors
            return {"message": "An error occurred inserting the item."}, 500  # Return Interval Server Error

        return {"message": "Stock created successfully."}, 201  # Return Successful Creation of Resource

    @staticmethod
    def put():
        data = StockRegister.parser.parse_args()
        item = StockModel.find_by_symbol(data['symbol'])

        item_to_put = StockModel(data['symbol'], data['prixch'], data['secxch'], data['active'])

        if item:
            try:
                item_to_put.update()

            except Exception as e:
                print('Error occurred - ', e)
                return {"message": "An error occurred updating the item."}, 500  # Return Interval Server Error

            return item_to_put.json()

        try:
            item_to_put.insert()

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred inserting the item."}, 500  # Return Interval Server Error

        return {"message": "Stock created successfully."}, 201  # Return Successful Creation of Resource


class StockList(Resource):

    @staticmethod
    def get(number_of_items="0"):
        try:
            items = StockModel.get_rows(number_of_items)

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while getting the items."}, 500  # Return Interval Server Error

        # return {'stocks': list(map(lambda x: x.json(), items))}  # we can map the list of objects,
        return {'stocks': [item.json() for item in items]}  # but this one is slightly more readable


class Stock(Resource):

    @staticmethod
    def get(symbol):

        try:
            item = StockModel.find_by_symbol(symbol)

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while getting the item."}, 500  # Return Interval Server Error

        if item:
            return item.json()

        return {'message': 'Item not found'}, 404  # Return Not Found

    # @jwt_required()
    @staticmethod
    def delete(symbol):

        try:
            StockModel.delete_symbol(symbol)

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while deleting the item."}, 500  # Return Interval Server Error

        return {'message': 'Item deleted'}
