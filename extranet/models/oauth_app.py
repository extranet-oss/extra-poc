import uuid
import json

from extranet import db
from extranet.models._templates import Dated

class OauthApp(Dated):

  # app credentials
  client_id = db.Column(db.String(36), index=True, unique=True, nullable=False)
  client_secret = db.Column(db.String(32), index=True, unique=True, nullable=False)

  # app settings
  is_confidential = db.Column(db.Boolean, nullable=False)
  _redirect_uris = db.Column(db.Text, name='redirect_uris', nullable=False)
  _default_scopes = db.Column(db.Text, name='default_scopes', nullable=False)

  # app info
  name = db.Column(db.String(255), index=True, nullable=False)
  description = db.Column(db.Text)
  website = db.Column(db.String(255), nullable=False)
  #picture = db.Column(db.ForeignKey('picture.id'))
  #picture = db.Column(db.ForeignKey('Picture'))

  # app owner
  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  owner = db.relationship('User')

  # flask_oauth stuff
  @property
  def client_type(self):
    if self.is_confidential:
      return 'confidential'
    return 'public'

  @property
  def redirect_uris(self):
    return json.loads(self._redirect_uris)

  @redirect_uris.setter
  def redirect_uris(self, value):
    self._redirect_uris = json.dumps(value)

  @property
  def default_redirect_uri(self):
    return self.redirect_uris[0]

  @property
  def default_scopes(self):
    return json.loads(self._default_scopes)

  @default_scopes.setter
  def default_scopes(self, value):
    self._default_scopes = json.dumps(value)

  def __repr__(self):
    return '<OauthApp %r>' % self.id