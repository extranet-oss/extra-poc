from flask import url_for
from requests_oauthlib import OAuth2Session

from extranet import app

REDIRECT_URI = 'https://' + app.config['OFFICE365_DOMAIN'] + '/auth/office365/'
AUTHORITY_URL = 'https://login.microsoftonline.com/common'
AUTHORIZE_ENDPOINT = '/oauth2/v2.0/authorize'
TOKEN_ENDPOINT = '/oauth2/v2.0/token'
RESOURCE_ID = 'https://graph.microsoft.com'
SCOPES = [ 'User.Read' ]
GRAPH_VER = 'v1.0'
GRAPH_URL = 'https://graph.microsoft.com/' + GRAPH_VER + '/'

client = OAuth2Session(app.config['OFFICE365_CLIENT_ID'],
                       redirect_uri = REDIRECT_URI,
                       scope = SCOPES)

def authorization_url():
  return client.authorization_url(AUTHORITY_URL + AUTHORIZE_ENDPOINT)

def fetch_token(code):
  return client.fetch_token(AUTHORITY_URL + TOKEN_ENDPOINT,
                            code = code,
                            client_secret = app.config['OFFICE365_CLIENT_SECRET'])

def get_from_graph(res):
  return client.get(GRAPH_URL + res)
