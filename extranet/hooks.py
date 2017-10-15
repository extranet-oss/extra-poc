from extranet import app, usm
from extranet import constants
from extranet.utils import version_tostring
from extranet.models.user import User

@app.after_request
def after_request(response):
  response.headers['Server'] = constants.APP_NAME + '/' + version_tostring(constants.APP_VERSION)
  return response

@usm.user_loader
def user_loader(uuid):
  return User.query.filter_by(uuid=uuid).first()