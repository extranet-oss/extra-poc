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

  def delete(self):
    db.session.delete(self)
    db.session.commit()
    return self

  @property
  def scopes(self):
    return json.loads(self._default_scopes)

  def __repr__(self):
    return '<OauthToken %r>' % self.id