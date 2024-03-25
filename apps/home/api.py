from run import api
from flask_restful import Resource
from apps.home.models import Product


class ProductAPI(Resource):
    def get(self):
        products = Product.get_json_list()
        return products

api.add_resource(ProductAPI, '/api/product/')