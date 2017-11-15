from flask import render_template, request
from flask_login import login_required, logout_user

from extranet.modules.auth import bp
from extranet.usm import anonymous_required, dirty_required
from extranet.utils import redirect_back


@bp.route('/login')
@anonymous_required
def login():
    return render_template('login.html')


@bp.route('/refresh')
@dirty_required
def refresh():
    return render_template('refresh.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect_back(request.args.get('next'), 'index')
