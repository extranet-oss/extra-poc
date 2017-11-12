from flask import render_template, request, flash, url_for
from flask_login import fresh_login_required, current_user, logout_user
import re

from extranet import db
from extranet.modules.auth import bp
from extranet.connections.intranet import client as intranet_client
from extranet.connections.intranet import no_token_required, IntranetInvalidToken, IntranetReadOnly
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
    current_user.unregister()
    logout_user()
    flash('Account deleted.')
    return url_for('index')

  # check autologin link format & extract token
  matches = autologin_regex.match(request.form.get('link'))
  if not matches:
    flash('An invalid autologin link was given.')
    return render_intranet()

  # fetch user info from intranet
  try:
    user_data = intranet_client.get_user(token=matches[1])
  except IntranetInvalidToken:
    flash('The autologin link is invalid or has expired.')
    return render_intranet()
  except:
    flash('Can\'t get user info from intranet.')
    return render_intranet()

  if user_data['login'] != current_user.intra_uid:
    flash('This isn\'t your intranet account.')
    return render_intranet()


  # start testing for write permissions
  # in order to do this, we test if we can modify user profile
  # no worry, we're feeding the intranet the same infos he'd given us earlier
  try:
    intranet_client.set_user_profile(user_data['userinfo'], user_data['login'], token=matches[1])
  except IntranetReadOnly:
    current_user.intra_token_rw = False
  except:
    flash('Can\'t get user info from intranet.')
    return render_intranet()
  else:
    current_user.intra_token_rw = True

  # intranet user is same as logged in user, saving token
  current_user.intra_token = matches[1]

  db.session.add(current_user)
  db.session.commit()

  return redirect_back(request.args.get('next'), 'index')