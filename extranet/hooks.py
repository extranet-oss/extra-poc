from extranet import app
from extranet import constants
from extranet.utils import version_tostring

@app.after_request
def after_request(response):
  response.headers['Server'] = constants.APP_NAME + '/' + version_tostring(constants.APP_VERSION)
  return response
