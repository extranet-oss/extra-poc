import uuid

from extranet import db
from extranet.models._templates import Base, Intra

# format: Country/City/Building/Room
# A building can be rooms by itself (see fr/par/samsung & fr/par/voltaire)
# A city can be rooms by itself (see fr/mpl)
# Disabled locations are not registered into the database, and are treated as unknown

class Country(Intra):

  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, unique=True, nullable=False)

  name = db.Column(db.String(255), nullable=False)

  cities = db.relationship('City', lazy=True, backref=db.backref('country', lazy=True), cascade='all, delete-orphan')
  buildings = db.relationship('Building', lazy=True, backref=db.backref('country', lazy=True), cascade='all, delete-orphan')
  rooms = db.relationship('Room', lazy=True, backref=db.backref('country', lazy=True), cascade='all, delete-orphan')

  def __init__(self, key, name):
    self.uuid = uuid.uuid4()
    self.intra_code = key

    self.name = name

  def __repr__(self):
    return '<Country %r>' % self.id


class City(Intra):

  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, unique=True, nullable=False)

  name = db.Column(db.String(255), nullable=False)

  country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)

  buildings = db.relationship('Building', lazy=True, backref=db.backref('city', lazy=True), cascade='all, delete-orphan')
  rooms = db.relationship('Room', lazy=True, backref=db.backref('city', lazy=True), cascade='all, delete-orphan')

  def __init__(self, key, name, country):
    self.uuid = uuid.uuid4()
    self.intra_code = key

    self.name = name

    self.country = country

  def __repr__(self):
    return '<City %r>' % self.id


class Building(Intra):

  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, unique=True, nullable=False)

  name = db.Column(db.String(255), nullable=False)

  country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
  city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)

  rooms = db.relationship('Room', lazy=True, backref=db.backref('building', lazy=True), cascade='all, delete-orphan')

  def __init__(self, key, name, country, city):
    self.uuid = uuid.uuid4()
    self.intra_code = key

    self.name = name

    self.country = country
    self.city = city

  def __repr__(self):
    return '<Building %r>' % self.id


room_types = db.Table('room_xref_room_type',
  db.Column('room_type_id', db.Integer, db.ForeignKey('room_type.id'), primary_key=True),
  db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True)
)


class Room(Intra):

  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, unique=True, nullable=False)

  name = db.Column(db.String(255), nullable=False)

  seats = db.Column(db.Integer, nullable=False)
  types = db.relationship('RoomType', secondary=room_types, lazy='subquery', backref=db.backref('rooms', lazy=True), cascade='all')

  country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
  city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
  building_id = db.Column(db.Integer, db.ForeignKey('building.id'))

  def __init__(self, key, name, seats, types, country=None, city=None, building=None):
    self.uuid = uuid.uuid4()
    self.intra_code = key

    self.name = name

    self.seats = seats
    self.types = types

    self.country = country
    self.city = city
    self.building = building

  def __repr__(self):
    return '<Room %r>' % self.id


class RoomType(Base):

  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, unique=True, nullable=False)
  name = db.Column(db.String(255), nullable=False)

  def __init__(self, key, name):
    self.uuid = uuid.uuid4()
    self.intra_code = key

    self.name = name

  def __repr__(self):
    return '<RoomType %r>' % self.id