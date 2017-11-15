# import dependencies
from flask import Blueprint

# define blueprint
bp = Blueprint('api_v0', __name__,
               url_prefix='/api/v0')

# load controllers
import extranet.modules.api.v0.controllers
