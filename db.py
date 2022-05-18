from flask_sqlalchemy import SQLAlchemy

# TODO: CHECK TIMEOUT
#  Certain database backends may impose different inactive connection timeouts, which interferes with
#  Flask-SQLAlchemy’s connection pooling.
#  set sqlalchemy db and options, below doesn't work for sqlite3
#  db = SQLAlchemy( engine_options={'connect_args': {'connect_timeout': 10}} )

db = SQLAlchemy()
