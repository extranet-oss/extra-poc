from flask import jsonify

from extranet.modules.api.v0 import bp
from extranet.constants import APP_NAME, APP_VERSION
from extranet.utils import external_url, version_tostring


@bp.route('/')
def index():
    return jsonify({
        'server': f'{APP_NAME}/{version_tostring(APP_VERSION)}',
        'version': 0,
        'homepage': external_url('/help/api/v0/')
    })
