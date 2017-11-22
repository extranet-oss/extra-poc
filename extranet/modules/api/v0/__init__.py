# import dependencies
from flask import Blueprint, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from extranet import app
from extranet.modules.api.v0.api import Api

limiter = Limiter(app, key_func=get_remote_address)

#@limiter.request_filter
#def ip_whitelist():
#    return request.remote_addr == "127.0.0.1"

# define blueprint
bp = Blueprint('api_v0', __name__,
               url_prefix='/api/v0')

api = Api(bp, limiter)

# load controllers
import extranet.modules.api.v0.schemas
import extranet.modules.api.v0.endpoints
