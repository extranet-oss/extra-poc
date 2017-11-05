import uuid

from extranet import db
from extranet.models._templates import Base

class Picture(Base):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)

  # picture metadata
  # origin can be:
  # - intra:<url>
  # - upload
  origin = db.Column(db.String(255), index=True, nullable=False)
  width = db.Column(db.Integer, nullable=False)
  height = db.Column(db.Integer, nullable=False)
  format = db.Column(db.String(255), nullable=False)

  # available sizes
  _sizes = db.Column(db.Text, name='sizes', nullable=False)

  def __init__(self, origin, width, height, format='png'):
    self.uuid = uuid.uuid4()

    self.origin = origin
    self.width = width
    self.height = height
    self.format = format

    self.sizes = []

  @property
  def sizes(self):
    return json.loads(self._sizes)

  @sizes.setter
  def sizes(self, value):
    self._sizes = json.dumps(value)

  def __repr__(self):
    return '<Picture %r>' % self.id