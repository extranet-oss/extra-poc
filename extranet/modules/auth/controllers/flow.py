from flask import render_template, redirect, url_for
from flask_login import login_required, logout_user

from extranet.modules.auth import bp
from extranet.usm import anonymous_required, dirty_required

@bp.route('/')
@anonymous_required
def login():
  return render_template('login.html')

@bp.route('/refresh/')
@dirty_required
def refresh():
  return render_template('refresh.html')

@bp.route('/logout/')
@login_required
def logout():
  logout_user()
  return redirect(url_for('index'))