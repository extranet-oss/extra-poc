from extranet.modules.oauthprovider import bp, provider

@bp.route('/revoke', methods=['POST'])
@provider.revoke_handler
def revoke_token():
  pass