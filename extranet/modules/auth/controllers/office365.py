from flask import session, request, redirect, url_for, flash
from flask_login import login_user, confirm_login, current_user
from werkzeug.security import gen_salt

from extranet import app, db
from extranet.modules.auth import bp
from extranet.modules.auth.helpers.office365 import build_external_url
from extranet.modules.auth.helpers.office365 import client as office365_client
from extranet.models.user import User
from extranet.usm import anonymous_or_dirty_required
from extranet.utils import redirect_back

@bp.route('/office365/')
@anonymous_or_dirty_required
def office365():
  # save parameters to session as office365 forbids parameters in return url
  session['office365.remember'] = request.args.get('remember') == "1"
  session['office365.next'] = request.args.get('next')
  session['office365.prev'] = 'auth.refresh' if current_user.is_authenticated else 'auth.login'

  # prevent csrf attacks
  session['office365.state'] = gen_salt(32)

  return office365_client.authorize(callback=build_external_url(url_for('auth.office365_authorized')),
                                    state=session['office365.state'])

@bp.route('/office365/authorized/')
@anonymous_or_dirty_required
def office365_authorized():
  # verify state
  if 'office365.state' not in session or session['office365.state'] != request.args.get('state'):
    flash('Invalid state.')
    return redirect(url_for(session['office365.prev']))

  # get response
  resp = office365_client.authorized_response()

  # check if response is valid
  if resp is None or not 'access_token' in resp:
    flash('You denied the request to sign in.')
    return redirect(url_for(session['office365.prev']))


  # define token for API requests
  token = (resp['access_token'], '')

  # fetch user info
  me = office365_client.get('me', token=token)
  if me.status != 200:
    flash("Failed to retrieve user data.")
    return redirect(url_for(session['office365.prev']))


  # if user is already logged in, confirm session
  if current_user.is_authenticated:

    # verify if user logged with the same account
    if current_user.office365_uid == me.data['id']:

      # everything ok, save new token & confirm login
      current_user.set_office365_token(token)

      db.session.add(current_user)
      db.session.commit()

      confirm_login()

      return redirect_back(session['office365.next'], 'index')
    else:
      flash("Please confirm your session with the same office365 account.")
      return redirect(url_for(session['office365.prev']))


  # no user logged in
  else:

    # get organizations membership info
    organization = office365_client.get('organization', token=token)
    if organization.status != 200:
      flash("Failed to retrieve user data.")
      return redirect(url_for(session['office365.prev']))

    # check if we got Epitech
    for org in organization.data['value']:
      if org['id'] in app.config['OFFICE365_ORGANIZATIONS']:

        user = User.query.filter_by(office365_uid=me.data['id']).first()

        # create user if not already registered
        if not user:

          user = User(me.data['mail'], me.data['givenName'], me.data['surname'])
          user.office365_uid = me.data['id']

        # everything ok, save token & login
        user.set_office365_token(token)

        db.session.add(user)
        db.session.commit()

        login_user(user, remember=session['office365.remember'], fresh=True)

        return redirect_back(session['office365.next'], 'index')

    flash("Please login with a valid Epitech account.")
    return redirect(url_for(session['office365.prev']))