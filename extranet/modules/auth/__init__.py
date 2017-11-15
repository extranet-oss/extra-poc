# import dependencies
from flask import Blueprint
from extranet import usm
from extranet.connections.intranet import client as intranet_client

# define blueprint
bp = Blueprint('auth', __name__,
               url_prefix='/auth',
               template_folder='templates')

# load controllers
import extranet.modules.auth.controllers

# configure user session manager
usm.login_view = 'auth.login'
usm.refresh_view = 'auth.refresh'

# configure intranet module
intranet_client.token_view = 'auth.intranet'
intranet_client.token_view_overrides += [
   'auth.refresh',
   'auth.login',
   'auth.logout',
   'auth.office365',
   'auth.office365_authorized'
]
