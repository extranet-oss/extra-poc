# import dependencies
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# create WSGI application object
app = Flask('extranet')

# load configuration
app.config.from_object('extranet.config')

# load database
db = SQLAlchemy(app)

# load database models
import extranet.models

# load login manager (named as User Session Manager)
usm = LoginManager(app)

# load modules
from extranet.modules.auth import bp as auth_module

# register modules
app.register_blueprint(auth_module)

# load hooks & cli
import extranet.hooks
import extranet.cli


# simple index page
from flask import render_template
@app.route('/')
def index():
  return render_template('index.html')