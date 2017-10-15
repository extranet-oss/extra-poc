# import dependencies
from flask import Blueprint

# define blueprint
bp = Blueprint('auth', __name__,
               url_prefix='/auth',
               template_folder='templates')

# load controllers
import extranet.modules.auth.controllers