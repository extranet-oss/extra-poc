# import dependencies
from flask import Blueprint

from extranet import app

# define blueprint
bp = Blueprint('oauthprovider', __name__,
               url_prefix='/oauth',
               template_folder='templates')

# configure oauth provider
app.config['OAUTH2_PROVIDER_ERROR_ENDPOINT'] = 'oauthprovider.error'

# load controllers
import extranet.modules.oauthprovider.controllers
