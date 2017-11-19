# import dependencies
from flask import Blueprint, request

from flask_limiter import Limiter
from flask_cors import CORS
from extranet import app

limiter = Limiter(app)

@limiter.request_filter
def ip_whitelist():
    return request.remote_addr == "127.0.0.1"

# define blueprint
bp = Blueprint('api_v0', __name__,
               url_prefix='/api/v0')

limiter.shared_limit(app.config['RATELIMIT_API'], 'api-v0')(bp)
CORS(bp, origins='*', send_wildcard=True)

# load controllers
import extranet.modules.api.v0.controllers
