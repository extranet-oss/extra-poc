from flask import render_template, request, flash, session
from flask_login import fresh_login_required
from werkzeug.security import gen_salt

from extranet.modules.oauthprovider import bp, provider
from extranet.models.oauth_app import OauthApp

def render_authorize(*args, **kwargs):
  app_id = kwargs.get('client_id')
  app = OauthApp.query.filter_by(client_id=app_id).first()
  kwargs['app'] = app

  session['oauthprovider.snitch'] = gen_salt(32)
  kwargs['snitch'] = session['oauthprovider.snitch']

  return render_template('authorize.html', **kwargs)

@bp.route('/authorize', methods=['GET', 'POST'])
@fresh_login_required
@provider.authorize_handler
def authorize(*args, **kwargs):
  if request.method == 'GET':
    return render_authorize(**kwargs)

  if 'oauthprovider.snitch' not in session or session['oauthprovider.snitch'] != request.form.get('snitch'):
    flash('Something went wrong, please retry.')
    return render_authorize(**kwargs)

  confirm = request.form.get('confirm', 'no')

  return confirm == 'yes'