from flask import render_template

from extranet.modules.oauthprovider import bp


@bp.route('/error')
def error():
    return render_template('error.html'), 400
