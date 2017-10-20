from extranet.modules.oauthprovider import bp, provider

@bp.route('/token', methods=['POST'])
@provider.token_handler
def access_token():
    return None