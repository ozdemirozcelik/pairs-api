from flask_restful import Resource, reqparse
from models.signals import SignalModel
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt


class SignalWebhook(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('passphrase',
                        type=str,
                        required=True,
                        help="This webhook needs a passphrase!"
                        )
    parser.add_argument('ticker',
                        type=str,
                        required=True,
                        help="This webhook needs a ticker!"
                        )
    parser.add_argument('order_action',
                        type=str,
                        required=True,
                        help="This webhook needs an order action!"
                        )
    parser.add_argument('order_contracts',
                        type=int,
                        required=True,
                        help="This webhook needs an order amount!"
                        )
    parser.add_argument('order_price',
                        type=float,
                        # required=True,
                        # help="This webhook needs an order price!"
                        )
    parser.add_argument('mar_pos',
                        type=str,
                        # required=True,
                        # help="This webhook needs an order action!"
                        )
    parser.add_argument('mar_pos_size',
                        type=int,
                        # required=True,
                        # help="This webhook needs a market position size!"
                        )
    parser.add_argument('pre_mar_pos',
                        type=str,
                        # required=True,
                        # help="This webhook needs an order action!"
                        )
    parser.add_argument('pre_mar_pos_size',
                        type=int,
                        # required=True,
                        # help="This webhook needs a previous market position size!"
                        )
    parser.add_argument('order_comment',
                        type=str,
                        default=""
                        )
    parser.add_argument('order_status',
                        type=str,
                        default="waiting"
                        )
    parser.add_argument('rowid',
                        type=int,
                        default=0
                        )

    @staticmethod
    def post():
        data = SignalWebhook.parser.parse_args()

        if SignalModel.passphrase_wrong(data['passphrase']):
            return {"message": "Passphrase incorrect."}, 400  # Return Bad Request

        item = SignalModel("", "", data['ticker'], data['order_action'], data['order_contracts'], data['order_price'],
                           data['mar_pos'], data['mar_pos_size'], data['pre_mar_pos'], data['pre_mar_pos_size'],
                           data['order_comment'], data['order_status'])

        try:
            item.insert()

        except Exception as e:
            print('Error occurred - ', e)  # better log the errors
            return {"message": "An error occurred inserting the item."}, 500  # Return Interval Server Error

        return {"message": "Signal created successfully."}, 201  # Return Successful Creation of Resource

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def put():
        data = SignalWebhook.parser.parse_args()

        if SignalModel.passphrase_wrong(data['passphrase']):
            return {"message": "Passphrase incorrect."}, 400  # Return Bad Request

        item = SignalModel.find_by_rowid(data['rowid'])

        if item:
            item_to_put = SignalModel("", "", data['ticker'], data['order_action'], data['order_contracts'],
                                      data['order_price'], data['mar_pos'], data['mar_pos_size'], data['pre_mar_pos'],
                                      data['pre_mar_pos_size'], data['order_comment'], data['order_status'])

            try:
                item_to_put.update(data['rowid'])

            except Exception as e:
                print('Error occurred - ', e)
                return {"message": "An error occurred updating the item."}, 500  # Return Interval Server Error

            item_to_put.rowid = data['rowid']
            return_json = item_to_put.json()

            return_json.pop('timestamp')

            return return_json

        return {"message": "No item found to update."}, 404  # Return Not Found


class SignalList(Resource):

    @staticmethod
    @jwt_required(optional=True)
    def get(number_of_items="0"):

        username = get_jwt_identity()

        # limit the number of items to get if not logged-in
        max_number_of_items = 5

        # TODO: check. without Authorization header, returns None.
        # with Authorization header, returns username
        if username is None:
            if number_of_items == "0":
                number_of_items = max(int(number_of_items), max_number_of_items)
            else:
                number_of_items = min(int(number_of_items), max_number_of_items)
        try:
            items = SignalModel.get_rows(str(number_of_items))

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while getting the items."}, 500  # Return Interval Server Error

        # return {'signals': list(map(lambda x: x.json(), items))}  # we can map the list of objects,
        return {'signals': [item.json() for item in items]}  # but this one is slightly more readable


class Signal(Resource):

    @staticmethod
    def get(rowid):

        try:
            item = SignalModel.find_by_rowid(rowid)

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while getting the item."}, 500  # Return Interval Server Error

        if item:
            return item.json()

        return {'message': 'Item not found'}, 404  # Return Not Found

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def delete(rowid):

        claims = get_jwt()

        # TODO: Delete only if admin
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401  # Return Unauthorized

        try:
            SignalModel.delete_name(rowid)

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while deleting the item."}, 500  # Return Interval Server Error

        return {'message': 'Item deleted'}
