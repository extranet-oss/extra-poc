from flask import render_template, request, flash
from flask_login import fresh_login_required, current_user
import re

from extranet import db
from extranet.modules.auth import bp
from extranet.connections.intranet import client as intranet_client
from extranet.connections.intranet import no_token_required
from extranet.utils import redirect_back

autologin_regex = re.compile('https://intra.epitech.eu/auth-([a-z0-9]{40})')

def render_intranet():
  return render_template('intranet.html')

@bp.route('/intranet', methods=['GET', 'POST'])
@fresh_login_required
@no_token_required
def intranet():
  if request.method == 'GET':
    return render_intranet()

  # check if user confirmed form
  if request.form.get('confirm') is None:
    flash('Something went wrong, please retry.')
    return render_intranet()
  confirm = request.form.get('confirm') == 'yes'

  if not confirm:
    # delete account, logout
    flash('You can\' delete your account yet.')
    return render_intranet()

  # check autologin link format & extract token
  matches = autologin_regex.match(request.form.get('link'))
  if not matches:
    flash('An invalid autologin link was given.')
    return render_intranet()

  # fetch user info from intranet
  r = intranet_client.get('user', token=matches[1])
  if r.status_code != 200:
    flash('Can\'t get user info from intranet.')
    return render_intranet()
  user = r.json()

  if user['login'] != current_user.email:
    flash('This isn\'t your intranet account.')
    return render_intranet()

  # intranet user is same as logged in user, saving token
  current_user.intra_uid = user['login']
  current_user.intra_token = matches[1]

  db.session.add(current_user)
  db.session.commit()

  return redirect_back(request.args.get('next'), 'index')