from flask import render_template, request, flash, session
from flask_login import login_required, current_user, login_fresh
from werkzeug.security import gen_salt

from extranet import usm
from extranet.modules.oauthprovider import bp
from extranet.connections.extranet import provider as extranet_provider
from extranet.connections.extranet import scopes as defined_scopes
from extranet.models.oauth_app import OauthApp
from extranet.models.oauth_token import OauthToken

def render_authorize(*args, **kwargs):
  app_id = kwargs.get('client_id')
  app = OauthApp.query.filter_by(client_id=app_id).first()
  kwargs['app'] = app

  session['oauthprovider.snitch'] = gen_salt(32)
  kwargs['snitch'] = session['oauthprovider.snitch']
  kwargs['request'] = request

  kwargs['defined_scopes'] = defined_scopes

  return render_template('authorize.html', **kwargs)

@bp.route('/authorize', methods=['GET', 'POST'])
@login_required
@extranet_provider.authorize_handler
def authorize(*args, **kwargs):
  # bypass accept/deny form if already accepted (has token)
  if OauthToken.query.filter_by(user_id=current_user.id).first() is not None:
    return True

  # confirm login to access autorize/deny dialog
  if not login_fresh():
    return usm.needs_refresh()

  # render accept/deny if GET request
  if request.method == 'GET':
    return render_authorize(*args, **kwargs)

  # verify POST request legitimacy
  if 'oauthprovider.snitch' not in session or session['oauthprovider.snitch'] != request.form.get('snitch'):
    flash('Something went wrong, please retry.')
    return render_authorize(*args, **kwargs)

  confirm = request.form.get('confirm', 'no')
  return confirm == 'yes'