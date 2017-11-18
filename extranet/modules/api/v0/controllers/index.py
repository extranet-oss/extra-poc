from flask import jsonify, g

from extranet.modules.api.v0 import bp, limiter
from extranet.constants import APP_NAME, APP_VERSION
from extranet.utils import external_url, version_tostring


@bp.route('/')
def index():
    current_limit = getattr(g, 'view_rate_limit', None)
    meta = {}
    if current_limit:
        window_stats = limiter.limiter.get_window_stats(*current_limit)
        reset_in = 1 + window_stats[0]
        meta['limit'] = current_limit[0].amount
        meta['remaining'] = window_stats[1]
        meta['reset'] = reset_in
    return jsonify({
        'server': f'{APP_NAME}/{version_tostring(APP_VERSION)}',
        'version': 0,
        'homepage': external_url('/help/api/v0/'),
        'meta': meta
    })
