from flask import render_template, request
from flask_login import fresh_login_required

from extranet.modules.oauthprovider import bp, provider
from extranet.models.oauth_app import OauthApp

@bp.route('/authorize', methods=['GET', 'POST'])
@fresh_login_required
@provider.authorize_handler
def authorize(*args, **kwargs):
  if request.method == 'GET':
    app_id = kwargs.get('client_id')
    app = OauthApp.query.filter_by(client_id=app_id).first()
    kwargs['app'] = app
    return render_template('authorize.html', **kwargs)

  confirm = request.form.get('confirm', 'no')

  return confirm == 'yes'