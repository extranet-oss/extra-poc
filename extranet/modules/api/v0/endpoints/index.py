from extranet.modules.api.v0 import api
from extranet.utils import external_url

@api.get('/', auth=False)
def get_index():
    return {
        'links': {
            'documentation': external_url('/help/api/v0/'),
            'self': api.url_for('get_index')
        }
    }
