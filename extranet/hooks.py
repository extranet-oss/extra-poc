from extranet import app
from extranet.constants import APP_NAME, APP_VERSION
from extranet.utils import version_tostring


@app.after_request
def after_request(response):
    response.headers['Server'] = f'{APP_NAME}/{version_tostring(APP_VERSION)}'
    return response
