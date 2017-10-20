# import dependencies
from flask import Blueprint
from flask_login import current_user
from flask_oauthlib.provider import OAuth2Provider
from flask_oauthlib.contrib.oauth2 import bind_cache_grant, bind_sqlalchemy

from extranet import app, db
from extranet.models.user import User
from extranet.models.oauth_app import OauthApp
from extranet.models.oauth_token import OauthToken

# define blueprint
bp = Blueprint('oauthprovider', __name__,
               url_prefix='/oauth',
               template_folder='templates')

# configure oauth provider
app.config['OAUTH2_PROVIDER_ERROR_ENDPOINT'] = 'oauthprovider.error'
provider = OAuth2Provider(app)

# configure stores
bind_sqlalchemy(provider, db.session, user=User, client=OauthApp, token=OauthToken)
def current_user_func():
  return User.query.filter_by(id=current_user.id).first()
bind_cache_grant(app, provider, current_user_func)

# load controllers
import extranet.modules.oauthprovider.controllers