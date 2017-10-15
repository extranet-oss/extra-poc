import uuid

from extranet import db
from extranet.models.base import Base

class User(Base):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)

  # basic user info
  email = db.Column(db.String(320), unique=True, nullable=False)
  username = db.Column(db.String(255), index=True, unique=True, nullable=False)
  realm = db.Column(db.String(253), nullable=False)
  firstname = db.Column(db.String(255), index=True, nullable=False)
  lastname = db.Column(db.String(255), index=True, nullable=False)

  # office365 user info
  office365_uid = db.Column(db.String(36), unique=True)
  office365_token = db.Column(db.Text)

  # intranet user info
  intra_uid = db.Column(db.String(320), unique=True)
  intra_token = db.Column(db.String(40))

  def __init__(self, email, firstname, lastname):
    self.uuid = uuid.uuid4()

    self.email = email
    self.firstname = firstname
    self.lastname = lastname

    self.username = self.email.split('@')[0]
    self.realm = self.email.split('@')[1]

  def __repr__(self):
    return '<User %r>' % self.id