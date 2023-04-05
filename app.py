"""
Pairs-Api by ozdemirozcelik
for details: https://github.com/ozdemirozcelik/pairs-api
"""

from flask import Flask
import configparser

# Create Flask application
app = Flask(__name__)

if __name__ == "__main__":  # to avoid duplicate calls
    app.run()

# get user configuration variables
configs = configparser.ConfigParser()
configs.read("config.ini")  # change to your config file name

import config  # global configuration
import security  # security module
import routes  # API resources
import handlers  # loaders and error handlers

# initialize SQLAlchemy
from db import db

db.init_app(app)

import demo  # front-end demo
