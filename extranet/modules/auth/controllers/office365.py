from flask import session, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required, confirm_login, current_user

from extranet import app, db
from extranet.modules.auth import bp
from extranet.modules.auth.helpers import office365 as oauth
from extranet.models.user import User
from extranet.usm import no_login_required, no_fresh_login_required
from extranet.utils import redirect_back

def office365_redirect():
  authorization_url, state = oauth.authorization_url()

  session['office365.state'] = state;
  session['office365.remember'] = request.args.get('remember') == "1";
  session['office365.next'] = request.args.get('next');

  return redirect(authorization_url)

def office365_verify():
  if 'office365.state' not in session or session['office365.state'] != request.args.get('state'):
    return "invalid state"

  token = oauth.fetch_token(request.args.get('code'))

  me = oauth.get_from_graph('/me').json()

  # if user is already logged in, confirm session
  if current_user.is_authenticated:
    if current_user.office365_uid == me['id']:
      current_user.office365_token = token

      db.session.add(current_user)
      db.session.commit()

      confirm_login()

      return redirect_back(session['office365.next'], 'index')
    else:
      flash("Please confirm your session with the same office365 account.")

      return redirect(url_for('auth.refresh'))

  else:

    organizations = oauth.get_from_graph('/organization').json()

    for organization in organizations['value']:
      if organization['id'] in app.config['OFFICE365_ORGANIZATIONS']:

        user = User.query.filter_by(office365_uid=me['id']).first()

        if not user:

          user = User(me['mail'], me['givenName'], me['surname'])
          user.office365_uid = me['id']

        user.office365_token = token

        db.session.add(user)
        db.session.commit()

        login_user(user, remember=session['office365.remember'], fresh=True)

        return redirect_back(session['office365.next'], 'index')

    flash("Please login with a valid Epitech account.")

  return redirect(url_for('auth.login'))

@bp.route('/office365/')
def office365():
  if not request.args.get('code'):
    return office365_redirect()
  else:
    return office365_verify()

@bp.route('/')
@no_login_required
def login():
  return render_template('login.html')

@bp.route('/refresh/')
@no_fresh_login_required
def refresh():
  return render_template('refresh.html')

@bp.route('/logout/')
@login_required
def logout():
  logout_user()
  return redirect(url_for('index'))