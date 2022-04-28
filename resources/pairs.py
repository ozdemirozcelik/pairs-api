from flask_restful import Resource, reqparse
from models.pairs import PairModel
from flask_jwt_extended import jwt_required, get_jwt


class PairRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name',
                        type=str,
                        required=True,
                        help="Name field cannot be empty!"
                        )
    parser.add_argument('hedge',
                        type=float,
                        required=True,
                        help="Hedge field cannot be empty!"
                        )
    parser.add_argument('status',
                        type=int,
                        default=0,
                        )

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def post():
        data = PairRegister.parser.parse_args()

        if PairModel.find_by_name(data['name']):
            return {"message": "Pair with that name already exists."}, 400  # Return Bad Request

        item = PairModel(data['name'], data['hedge'], data['status'])

        try:
            item.insert()

        except Exception as e:
            print('Error occurred - ', e)  # better log the errors
            return {"message": "An error occurred inserting the item."}, 500  # Return Interval Server Error

        return {"message": "Pair created successfully."}, 201  # Return Successful Creation of Resource

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def put():
        data = PairRegister.parser.parse_args()

        item = PairModel(data['name'], data['hedge'], data['status'])

        if PairModel.find_by_name(data['name']):
            try:
                item.update()

            except Exception as e:
                print('Error occurred - ', e)
                return {"message": "An error occurred updating the item."}, 500  # Return Interval Server Error

            return item.json()

        try:
            item.insert()

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred inserting the item."}, 500  # Return Interval Server Error

        return {"message": "Pair created successfully."}, 201  # Return Successful Creation of Resource


class PairList(Resource):

    @staticmethod
    def get(number_of_items="0"):
        try:
            items = PairModel.get_rows(number_of_items)

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while getting the items."}, 500  # Return Interval Server Error

        # return {'pairs': list(map(lambda x: x.json(), items))}  # we can map the list of objects,
        return {'pairs': [item.json() for item in items]}  # but this one is slightly more readable


class Pair(Resource):

    @staticmethod
    def get(name):

        try:
            item = PairModel.find_by_name(name)

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while getting the item."}, 500  # Return Interval Server Error

        if item:
            return item.json()

        return {'message': 'Item not found'}, 404  # Return Not Found

    @staticmethod
    @jwt_required(fresh=True)  # need fresh token
    def delete(name):

        claims = get_jwt()

        # TODO: Delete only if admin
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401  # Return Unauthorized

        try:
            item_to_delete = PairModel.find_by_name(name)

            if item_to_delete:
                item_to_delete.delete()
            else:
                return {'message': 'No item to delete'}

        except Exception as e:
            print('Error occurred - ', e)
            return {"message": "An error occurred while deleting the item."}, 500  # Return Interval Server Error

        return {'message': 'Item deleted'}
