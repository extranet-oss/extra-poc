from extranet.modules.api.v0 import api
from extranet.modules.api.v0.api.utils import api_url
from extranet.utils import external_url

@api.get('/', auth=False)
def get_index():
    return {
        'links': {
            'documentation': external_url('/help/api/v0/'),
            'self': api_url('get_index')
        }
    }
