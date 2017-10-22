from flask import render_template, request, flash, session
from flask_login import login_required, current_user, login_fresh
from werkzeug.security import gen_salt

from extranet import usm
from extranet.modules.oauthprovider import bp, provider
from extranet.models.oauth_app import OauthApp
from extranet.models.oauth_token import OauthToken

def render_authorize(*args, **kwargs):
  app_id = kwargs.get('client_id')
  app = OauthApp.query.get(app_id)
  kwargs['app'] = app

  session['oauthprovider.snitch'] = gen_salt(32)
  kwargs['snitch'] = session['oauthprovider.snitch']

  return render_template('authorize.html', **kwargs)

@bp.route('/authorize', methods=['GET', 'POST'])
@login_required
@provider.authorize_handler
def authorize(*args, **kwargs):
  # bypass accept/deny form if already accepted (has token)
  if OauthToken.query.get(current_user.id) is not None:
    return True

  # confirm login to access autorize/deny dialog
  if not login_fresh():
    return usm.needs_refresh()

  # render accept/deny if GET request
  if request.method == 'GET':
    return render_authorize(**kwargs)

  # verify POST request legitimacy
  if 'oauthprovider.snitch' not in session or session['oauthprovider.snitch'] != request.form.get('snitch'):
    flash('Something went wrong, please retry.')
    return render_authorize(**kwargs)

  confirm = request.form.get('confirm', 'no')
  return confirm == 'yes'