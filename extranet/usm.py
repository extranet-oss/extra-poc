from functools import wraps
from flask import abort
from flask_login import LoginManager, current_user, login_fresh

from extranet import app
from extranet.models.user import User

usm = LoginManager(app)


@usm.user_loader
def user_loader(uuid):
    return User.query.filter_by(uuid=uuid).first()


# for views that require no login at all
def anonymous_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if usm._login_disabled:
            return func(*args, **kwargs)
        elif current_user.is_authenticated:
            return abort(401)
        return func(*args, **kwargs)
    return decorated_view


# for views that require a non-fresh login
def dirty_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if usm._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return usm.unauthorized()
        elif login_fresh():
            return abort(401)
        return func(*args, **kwargs)
    return decorated_view


# for views that either require anonymous or dirty login
def anonymous_or_dirty_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if usm._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return func(*args, **kwargs)
        elif not login_fresh():
            return func(*args, **kwargs)
        return abort(401)
    return decorated_view
