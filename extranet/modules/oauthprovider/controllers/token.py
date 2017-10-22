from extranet.modules.oauthprovider import bp
from extranet.connections.extranet import provider as extranet_provider

@bp.route('/token', methods=['POST'])
@extranet_provider.token_handler
def access_token():
    return None