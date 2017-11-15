from extranet.modules.oauthprovider import bp
from extranet.connections.extranet import provider as extranet_provider


@bp.route('/revoke', methods=['POST'])
@extranet_provider.revoke_handler
def revoke_token():
    pass
