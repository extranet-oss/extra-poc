from extranet import db
from extranet.models._templates import Base, Intra

# format: Country/City/Building/Room
# A building can be rooms by itself (see fr/par/samsung & fr/par/voltaire)
# A city can be rooms by itself (see fr/mpl)
# Disabled locations are not registered into the database, and are treated as unknown

class Country(Intra):

  intra_code = db.Column(db.String(255), index=True, unique=True, nullable=False)

  code = db.Column(db.String(2), index=True, unique=True, nullable=False)
  name = db.Column(db.String(255), nullable=False)

  cities = db.relationship('City', lazy=True, backref=db.backref('country', lazy=True))
  buildings = db.relationship('Building', lazy=True, backref=db.backref('country', lazy=True))
  rooms = db.relationship('Room', lazy=True, backref=db.backref('country', lazy=True))

  def __init__(self, key, code, name):
    self.intra_code = key

    self.code = self.normalize_code(code)
    self.name = name

  @staticmethod
  def normalize_code(code):
    return code.lower()

  def __repr__(self):
    return '<Country %r>' % self.id


class City(Intra):

  intra_code = db.Column(db.String(255), index=True, unique=True, nullable=False)

  code = db.Column(db.String(3), index=True, unique=True, nullable=False)
  name = db.Column(db.String(255), nullable=False)

  country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)

  buildings = db.relationship('Building', lazy=True, backref=db.backref('city', lazy=True))
  rooms = db.relationship('Room', lazy=True, backref=db.backref('city', lazy=True))

  def __init__(self, key, code, name, country):
    self.intra_code = key

    self.code = self.normalize_code(code)
    self.name = name

    self.country = country

  @staticmethod
  def normalize_code(code):
    return code.lower()

  def __repr__(self):
    return '<City %r>' % self.id


class Building(Intra):

  intra_code = db.Column(db.String(255), index=True, unique=True, nullable=False)

  code = db.Column(db.String(255), index=True, nullable=False)
  name = db.Column(db.String(255), nullable=False)

  country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
  city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)

  rooms = db.relationship('Room', lazy=True, backref=db.backref('building', lazy=True))

  def __init__(self, key, code, name, country, city):
    self.intra_code = key

    self.code = self.normalize_code(code)
    self.name = name

    self.country = country
    self.city = city

  @staticmethod
  def normalize_code(code):
    return code.lower().replace('-', '_')

  def __repr__(self):
    return '<Building %r>' % self.id


room_types = db.Table('room_xref_room_type',
  db.Column('room_type_id', db.Integer, db.ForeignKey('room_type.id'), primary_key=True),
  db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True)
)


class Room(Intra):

  intra_code = db.Column(db.String(255), index=True, unique=True, nullable=False)

  code = db.Column(db.String(255), index=True, nullable=False)
  name = db.Column(db.String(255), nullable=False)

  seats = db.Column(db.Integer, nullable=False)
  types = db.relationship('RoomType', secondary=room_types, lazy='subquery', backref=db.backref('rooms', lazy=True))

  country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
  city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
  building_id = db.Column(db.Integer, db.ForeignKey('building.id'))

  def __init__(self, key, code, name, seats, types, country=None, city=None, building=None):
    self.intra_code = key

    self.code = self.normalize_code(code)
    self.name = name

    self.seats = seats
    self.types = types

    self.country = country
    self.city = city
    self.building = building

  @staticmethod
  def normalize_code(code):
    return code.lower().replace('-', '_')

  def __repr__(self):
    return '<Room %r>' % self.id


class RoomType(Base):

  code = db.Column(db.String(255), index=True, unique=True, nullable=False)
  name = db.Column(db.String(255), nullable=False)

  def __init__(self, code, name):
    self.code = self.normalize_code(code)
    self.name = name

  @staticmethod
  def normalize_code(code):
    return code.lower().replace('-', '_')

  def __repr__(self):
    return '<RoomType %r>' % self.id