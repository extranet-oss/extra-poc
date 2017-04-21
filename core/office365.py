from requests_oauthlib import OAuth2Session
import requests

CLIENT_ID = r'f48f64d6-b249-4fea-9f01-005389e640ab'
CLIENT_SECRET = r'fCZptJNqVvcRO1FhCreVW0t'
REDIRECT_URI = 'https://extranet.epi.codes/login/office365/auth/'
AUTHORITY_URL = 'https://login.microsoftonline.com/common'
AUTHORIZE_ENDPOINT = '/oauth2/v2.0/authorize'
TOKEN_ENDPOINT = '/oauth2/v2.0/token'
RESOURCE_ID = 'https://graph.microsoft.com'
SCOPES = ['user.read']

#GRAPH_URL = 'https://graph.windows.net'
#GRAPH_VER = '1.6'
GRAPH_URL = 'https://graph.microsoft.com'
GRAPH_VER = 'v1.0'

oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)

def authorization_url():
  return oauth.authorization_url(AUTHORITY_URL + AUTHORIZE_ENDPOINT)

def fetch_token(code):
  return oauth.fetch_token(AUTHORITY_URL + TOKEN_ENDPOINT, code=code, client_secret=CLIENT_SECRET)

def get_from_graph(res, token):
  headers = {
    'Authorization': oauth.token['token_type']+' '+oauth.token['access_token'],
    'Content-Type': 'application/json'
  }
  print(headers)
  #return requests.request('GET', GRAPH_URL+res+"?api-version="+GRAPH_VER, headers=headers)
  return requests.request('GET', GRAPH_URL+"/"+GRAPH_VER+res, headers=headers)
