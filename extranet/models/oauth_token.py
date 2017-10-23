import uuid
import json

from extranet import db
from extranet.models._templates import Base

class OauthToken(Base):

  # associated application
  client_id = db.Column(db.String(36), db.ForeignKey('oauth_app.client_id'), nullable=False)
  client = db.relationship('OauthApp')

  # token info
  token_type = db.Column(db.String(40), nullable=False)
  expires = db.Column(db.DateTime, nullable=False)
  _scopes = db.Column(db.Text, name='scopes', nullable=False)

  # token strings
  access_token = db.Column(db.String(255), unique=True, nullable=False)
  refresh_token = db.Column(db.String(255), unique=True, nullable=False)

  # associated user
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  user = db.relationship('User')

  def __init__(self, *args, **kwargs):
    self.access_token = kwargs.get('access_token')
    self.token_type = kwargs.get('token_type')
    self.refresh_token = kwargs.get('refresh_token')
    self.scopes = kwargs.get('scope').split()

  def delete(self):
    db.session.delete(self)
    db.session.commit()
    return self

  @property
  def scopes(self):
    return json.loads(self._scopes)

  @scopes.setter
  def scopes(self, scopes):
    self._scopes = json.dumps(scopes)

  def __repr__(self):
    return '<OauthToken %r>' % self.id