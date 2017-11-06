import uuid

from extranet import db
from extranet.models._templates import Intra

class School(Intra):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, nullable=False)

  # school info
  code = db.Column(db.String(255), nullable=False)
  name = db.Column(db.String(255), nullable=False)

  def __init__(code, name):
    self.uuid = uuid.uuid4()
    self.intra_code = code

    self.code = self.normalize_code(code)
    self.name = name

  @staticmethod
  def normalize_code(code):
    return code.lower().replace('-', '_')

  def __repr__(self):
    return '<School %r>' % self.id


class Promotion(Intra):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, nullable=False)

  # promo info
  code = db.Column(db.Integer, nullable=False)
  name = db.Column(db.String(255), nullable=False)

  def __init__(code, name):
    self.uuid = uuid.uuid4()
    self.intra_code = code

    self.code = self.normalize_code(code)
    self.name = name

  @staticmethod
  def normalize_code(code):
    return int(code)

  def __repr__(self):
    return '<Promotion %r>' % self.id


class Course(Intra):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, nullable=False)

  # course info
  code = db.Column(db.String(255), nullable=False)
  name = db.Column(db.String(255), nullable=False)

  def __init__(code, name):
    self.uuid = uuid.uuid4()
    self.intra_code = code

    self.code = self.normalize_code(code)
    self.name = name

  @staticmethod
  def normalize_code(code):
    return code.lower().replace('/', '_').replace('-', '_')

  def __repr__(self):
    return '<Course %r>' % self.id