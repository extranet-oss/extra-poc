# import dependencies
from flask_login import current_user
from flask_oauthlib.provider import OAuth2Provider
from flask_oauthlib.contrib.oauth2 import bind_cache_grant, bind_sqlalchemy

from extranet import app, db
from extranet.models.user import User
from extranet.models.oauth_app import OauthApp
from extranet.models.oauth_token import OauthToken

# configure oauth provider
provider = OAuth2Provider(app)

# configure stores
bind_sqlalchemy(provider, db.session, user=User, client=OauthApp, token=OauthToken)

def current_user_func():
  return User.query.get(current_user.id)
bind_cache_grant(app, provider, current_user_func)

scopes = {
  'user.read': {
    'description_brief': "Read your profile",
    'description': "This app will be able to read your basic profile information, such as names, promotion or city"
  }
}