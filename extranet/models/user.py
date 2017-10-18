import uuid
import json

from extranet import db
from extranet.models._templates import Dated

class User(Dated):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  active = db.Column(db.Boolean, nullable=False)

  # basic user info
  email = db.Column(db.String(320), unique=True, nullable=False)
  username = db.Column(db.String(255), index=True, unique=True, nullable=False)
  realm = db.Column(db.String(253), nullable=False)
  firstname = db.Column(db.String(255), index=True, nullable=False)
  lastname = db.Column(db.String(255), index=True, nullable=False)

  # office365 user info
  office365_uid = db.Column(db.String(36), unique=True)
  _office365_token = db.Column(db.Text, name='office365_token')

  # intranet user info
  intra_uid = db.Column(db.String(320), unique=True)
  intra_token = db.Column(db.String(40))

  def __init__(self, email, firstname, lastname):
    self.uuid = uuid.uuid4()
    self.active = True

    self.email = email
    self.firstname = firstname
    self.lastname = lastname

    self.username = self.email.split('@')[0]
    self.realm = self.email.split('@')[1]

  # usm stuff
  @property
  def is_active(self):
      return self.active

  @property
  def is_authenticated(self):
      return True

  @property
  def is_anonymous(self):
      return False

  def get_id(self):
    return self.uuid

  # office tokens
  @property
  def office365_token(self):
    return json.loads(self._office365_token)

  @office365_token.setter
  def office365_token(self, token):
    self._office365_token = json.dumps(token)

  def __repr__(self):
    return '<User %r>' % self.id