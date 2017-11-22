from extranet.modules.api.v0 import api
from extranet.modules.api.v0.api.utils import auth
from extranet.connections.intranet import client

@api.get('/me/', scopes=['user.read'])
def get_me():
    return {
        'data': client.get('user', token=auth['user'].intra_token),
        'links': {
            'self': api.url_for('get_me')
        }
    }
