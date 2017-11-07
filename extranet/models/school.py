import uuid

from extranet import db
from extranet.models._templates import Intra

class School(Intra):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, nullable=False)

  # school info
  name = db.Column(db.String(255), nullable=False)

  def __init__(code, name):
    self.uuid = uuid.uuid4()
    self.intra_code = code

    self.name = name

  def __repr__(self):
    return '<School %r>' % self.id


class Promotion(Intra):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, nullable=False)

  # promo info
  name = db.Column(db.String(255), nullable=False)

  def __init__(code, name):
    self.uuid = uuid.uuid4()
    self.intra_code = code

    self.name = name

  def __repr__(self):
    return '<Promotion %r>' % self.id


class Course(Intra):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, nullable=False)

  # course info
  name = db.Column(db.String(255), nullable=False)

  def __init__(code, name):
    self.uuid = uuid.uuid4()
    self.intra_code = code

    self.name = name

  def __repr__(self):
    return '<Course %r>' % self.id