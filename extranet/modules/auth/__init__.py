# import dependencies
from flask import Blueprint
from extranet import usm

# define blueprint
bp = Blueprint('auth', __name__,
               url_prefix='/auth',
               template_folder='templates')

# load controllers
import extranet.modules.auth.controllers

# configure user session manager
usm.login_view = 'auth.login'
usm.refresh_view = 'auth.refresh'