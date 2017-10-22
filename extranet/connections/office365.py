from flask import request
from flask_oauthlib.client import OAuth
from flask_login import current_user

from extranet import app

oauth = OAuth()
client = oauth.remote_app(
  'office365',
  request_token_params = {
    'scope': 'User.Read'
  },
  base_url = 'https://graph.microsoft.com/v1.0/',
  access_token_method = 'POST',
  access_token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
  authorize_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
  app_key = 'OFFICE365'
)

@client.tokengetter
def office365_tokengetter(token = None):
  if token is not None:
    return token

  try:
    return request.oauth.user.office365_token
  except AttributeError:
    pass

  if current_user.is_authenticated:
    return current_user.office365_token

  return None