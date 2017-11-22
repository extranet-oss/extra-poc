from extranet.modules.api.v0 import api
from extranet.utils import external_url

@api.get('index', '/', auth=False)
def index():
    return {
        'links': {
            'documentation': external_url('/help/api/v0/'),
            'self': api.url_for('index')
        }
    }
