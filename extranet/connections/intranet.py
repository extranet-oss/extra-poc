from functools import wraps
from flask import url_for, request, redirect, abort
from flask_login import current_user
import requests

from extranet import app
from extranet.constants import APP_NAME, APP_VERSION
from extranet.utils import external_url, version_tostring

class IntranetException(RuntimeError):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return self.message

class Intranet():

  base_url = 'https://intra.epitech.eu/auth-'
  useragent = 'Mozilla/5.0 (compatible; ' + APP_NAME + '/' + version_tostring(APP_VERSION) + '; +' + external_url('/bot') + ')'

  cookies = {
    'language': 'en',
    'tz': 'UTC'
  }

  def __init__(self, app=None):
    self._token_getter = None
    self._has_token_checker = None

    self.token_view = None
    self.token_view_overrides = ['static']

    if app is not None:
      self.init_app(app)

  def init_app(self, app):
    app.before_request(self._before_request)

  def get(self, *args, **kwargs):
    kwargs['method'] = 'GET'
    return self.request(*args, **kwargs)

  def post(self, *args, **kwargs):
    kwargs['method'] = 'POST'
    return self.request(*args, **kwargs)

  def request(self, url, data=None, format='json', method='GET', token=None):

    headers = {
      'User-Agent': self.useragent
    }

    if token is None:
      token = self.get_request_token()

    target = self.base_url + token + '/' + url

    params = {}
    if method == 'GET':
      params = dict(data or {})
      data = None

    params['format'] = format

    return requests.request(method, target, params=params, data=data, headers=headers, cookies=self.cookies)

  def token_getter(self, f):
    self._token_getter = f
    return f

  def has_token_checker(self, f):
    self._has_token_checker = f
    return f

  def get_request_token(self):
    assert self._token_getter is not None, 'missing tokengetter'

    token = self._token_getter()
    if token is None:
      raise IntranetException('No token available')

    return token

  def _before_request(self):
    if self._has_token_checker is None or self.token_view is None:
      return

    if request.endpoint != self.token_view and request.endpoint not in self.token_view_overrides and self._has_token_checker() is False:
      return redirect(url_for(self.token_view, next=request.full_path))

client = Intranet(app)

@client.token_getter
def token_getter():

  try:
    return request.oauth.user.intra_token
  except AttributeError:
    pass

  if current_user.is_authenticated:
    return current_user.intra_token

  return None

@client.has_token_checker
def has_token_checker():

  if current_user.is_authenticated:
    return current_user.intra_token is not None

  return None

def no_token_required(func):
  @wraps(func)
  def decorated_view(*args, **kwargs):
    if has_token_checker():
      return abort(401)
    return func(*args, **kwargs)
  return decorated_view