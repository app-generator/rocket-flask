# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from   flask_migrate import Migrate
from   flask_minify  import Minify
from   sys import exit
from flask import jsonify
from apps.config import config_dict
from apps import create_app, db
from celery import Celery, Task
from flask_restful import Resource, Api
from apps.home.models import Product

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')


flask_app = create_app(app_config)
celery_app = flask_app.extensions["celery"]

api = Api(flask_app)

class ProductAPI(Resource):
    def get(self):
        products = Product.get_json_list()
        return products

api.add_resource(ProductAPI, '/api/product/')

Migrate(flask_app, db)

if not DEBUG:
    Minify(app=flask_app, html=True, js=False, cssless=False)
    
if DEBUG:
    flask_app.logger.info('DEBUG            = ' + str(DEBUG) )
    flask_app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    flask_app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)

if __name__ == "__main__":
    flask_app.run()
