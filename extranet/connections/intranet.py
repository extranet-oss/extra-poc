from functools import wraps
from flask import url_for, request, redirect, abort
from flask_login import current_user
import requests
import json
from PIL import Image

from extranet import app
from extranet.constants import APP_NAME, APP_VERSION
from extranet.utils import external_url, version_tostring

class IntranetError(RuntimeError):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return self.message

class IntranetInvalidResponse(IntranetError):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return self.message

class IntranetInvalidToken(IntranetError):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return self.message

class IntranetNotFound(IntranetError):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return self.message

class IntranetForbidden(IntranetError):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return self.message

class IntranetReadOnly(IntranetError):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return self.message

EXCEPTION_MAP = {
  'Your authentication code does not exist or has expired. Please connect again with your regular user name and details.': IntranetInvalidToken,
  'No unit corresponding to your request': IntranetNotFound,
  'This activity doesn\'t exist': IntranetNotFound,
  'Page not found': IntranetNotFound,
  'This event does not exist or was removed': IntranetNotFound,
  'You are not allowed to access other students\' information': IntranetForbidden,
  'Vous êtes connecté en tant que parent, seul l\'étudiant peut effectuer cette action': IntranetReadOnly
}

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

  def get(self, url, **kwargs):
    kwargs['method'] = 'GET'
    return self.request(url, **kwargs)

  def post(self, url, **kwargs):
    kwargs['method'] = 'POST'
    return self.request(url, **kwargs)

  def request(self, url, data=None, format='json', method='GET', token=None, raw=False):

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

    r = requests.request(method, target, params=params, data=data, headers=headers, cookies=self.cookies)

    if not r.ok:
      error_message = 'HTTP/{} "{}" recieved'.format(r.status_code, r.reason)

      try:
        data = r.json()

        if 'error' in data:
          error_message = data['error']
        elif 'message' in data:
          error_message = data['message']

        if error_message in EXCEPTION_MAP:
          raise EXCEPTION_MAP[error_message](error_message)
        else:
          raise IntranetError(error_message)
      except ValueError:
          raise IntranetError(error_message)

    if not raw:
      if format == 'json':
        try:
          return r.json()
        except ValueError:
          raise IntranetInvalidResponse('Invalid JSON recieved')

    return r.text

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
      raise IntranetError('No token available')

    return token

  def _before_request(self):
    if self._has_token_checker is None or self.token_view is None:
      return

    if request.endpoint != self.token_view and request.endpoint not in self.token_view_overrides and self._has_token_checker() is False:
      return redirect(url_for(self.token_view, next=request.full_path))

  def get_locations(self, **kwargs):
    kwargs['raw'] = True
    js = self.get('location.js', **kwargs)

    # find bounds of json object inside js code
    start = js.find('{')
    if start == -1:
      start = 0
    end = js.find('};')
    if end != -1:
      end += 1

    # extract json data
    try:
      return json.loads(js[start:end])
    except:
      raise IntranetInvalidResponse('Invalid JSON recieved')

  def get_current_user(self, **kwargs):
    data = self.get('user/', **kwargs)
    return data['login']

  def get_user(self, login=None, **kwargs):
    url = 'user'
    if login is not None:
      url = 'user/{}/'.format(login)

    return self.get(url, **kwargs)

  def get_all_users(self, **kwargs):
    return self.get('complete/user', **kwargs)

  def get_picture(self, login=None):
    if login is None:
      login = self.get_current_user(**kwargs)

    url = 'https://cdn.local.epitech.eu/userprofil/{}.bmp'.format(login.split('@')[0])
    r = requests.get(url, stream=True, headers={
      'User-Agent': self.useragent
    })
    if not r.ok:
      if r.status_code == 404:
        raise IntranetNotFound('Picture not found')
      else:
        raise IntranetError('HTTP/{} "{}" recieved'.format(r.status_code, r.reason))

    r.raw.decode_content = True
    try:
      return Image.open(r.raw)
    except IOError:
      raise IntranetInvalidResponse('Invalid image recieved')

  def set_user_profile(self, data, login=None, **kwargs):
    if login is None:
      login = self.get_current_user(**kwargs)

    # We need to format those stupid parameters
    payload = {}
    for name, info in data.items():
      payload['{}[name]'.format(name)] = name
      payload['{}[value]'.format(name)] = info['value']

      if 'public' in info and info['public']:
        payload['{}[public]'.format(name)] = 'on'
      else:
        payload['{}[public]'.format(name)] = ''

      if 'adm' in info and info['adm']:
        payload['{}[adm]'.format(name)] = 'on'
      else:
        payload['{}[adm]'.format(name)] = ''
    kwargs['data'] = payload

    return self.post('user/{}/edit/save'.format(login), **kwargs)

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