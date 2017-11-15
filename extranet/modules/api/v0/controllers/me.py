from flask import jsonify

from extranet.modules.api.v0 import bp
from extranet.connections.extranet import provider as extranet_provider
from extranet.connections.intranet import client as intranet_client


@bp.route('/me')
@extranet_provider.require_oauth('user.read')
def me():
    return jsonify(intranet_client.get('user'))
