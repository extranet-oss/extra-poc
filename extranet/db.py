from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

from extranet import app

# Setup db
db = SQLAlchemy(app)

# Set UTC timezone for every connections
#
# We're not using this method because variable is set multiple times
# through a single connection
#@event.listens_for(db.engine, 'engine_connect')
#def connect_event(connection, branch):
#  connection.execute('SET time_zone = "+00:00";')

# Set UTC timezone for every connections
#
# This method is called once when the db connection is created, but this may be
# not compatible trough systems because it uses directly the underlying DBAPI
# (methods could change)
@event.listens_for(db.engine, 'connect')
def connect_event(dbapi_connection, connection_record):
  dbapi_connection.query('SET time_zone = "+00:00";')