from flask import session, request, redirect

from extranet import app
from extranet.modules.auth import bp
from extranet.modules.auth.helpers import office365 as oauth

def office365_redirect():
  authorization_url, state = oauth.authorization_url()

  session['office365.state'] = state;

  return redirect(authorization_url)

def office365_verify():
  if 'office365.state' not in session or session['office365.state'] != request.args.get('state'):
    return "invalid state"

  token = oauth.fetch_token(request.args.get('code'))

  data = {
    'me': oauth.get_from_graph('/me').json(),
    'organization': oauth.get_from_graph('/organization').json()
  }

  for organization in data['organization']['value']:
    if organization['id'] in app.config['OFFICE365_ORGANIZATIONS']:
      return "OK, you're from Epitech."
  return "FAIL, you're not from Epitech"

@bp.route('/office365/')
def office365():
  if not request.args.get('code'):
    return office365_redirect()
  else:
    return office365_verify()