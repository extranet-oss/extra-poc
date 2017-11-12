import uuid
import json
from enum import Enum, auto
from slugify import slugify

from extranet import db
from extranet.models._templates import Dated, Intra


#
# Associate user with groups
#
user_groups = db.Table('user_xref_user_group',
  db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
  db.Column('user_group_id', db.Integer, db.ForeignKey('user_group.id'), primary_key=True)
)


#
# User basic data
#
class User(Intra):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  registered = db.Column(db.Boolean, nullable=False, default=False)
  active = db.Column(db.Boolean, nullable=False, default=True)

  # basic user info
  username = db.Column(db.String(255), index=True, unique=True, nullable=False)
  realm = db.Column(db.String(253), nullable=False)
  fullname = db.Column(db.String(255), index=True, nullable=False)
  public = db.Column(db.Boolean, nullable=False, default=False)

  # profile pic
  picture_id = db.Column(db.Integer, db.ForeignKey('picture.id'))
  picture = db.relationship('Picture', lazy=True, backref=db.backref('user', lazy=True), cascade='all, delete-orphan', single_parent=True)

  # registered user info
  rtime = db.Column(db.DateTime)
  email = db.Column(db.String(320), unique=True)
  firstname = db.Column(db.String(255))
  lastname = db.Column(db.String(255))

  # office365 user info
  office365_uid = db.Column(db.String(36), unique=True)
  _office365_token = db.Column(db.Text, name='office365_token')

  # intranet user info
  intra_uid = db.Column(db.String(320), index=True, unique=True, nullable=False)
  intra_token = db.Column(db.String(40))
  ctime = db.Column(db.DateTime)
  mtime = db.Column(db.DateTime)

  # relations
  custom_infos = db.relationship('UserProfileCustomInfo', lazy=True, backref=db.backref('user', lazy=True), cascade='all, delete-orphan')
  groups = db.relationship('UserGroup', secondary=user_groups, lazy=True, backref=db.backref('users', lazy=True))
  managed_groups = db.relationship('UserGroup', lazy=True, backref=db.backref('master', lazy=True), cascade='all, delete-orphan')
  academic = db.relationship('UserAcademic', lazy=True, backref=db.backref('user', lazy=True), cascade='all, delete-orphan', uselist=False)
  oauth_apps = db.relationship('OauthApp', lazy=True, backref=db.backref('owner', lazy=True), cascade='all, delete-orphan')
  oauth_tokens = db.relationship('OauthToken', lazy=True, backref=db.backref('user', lazy=True), cascade='all, delete-orphan')

  def __init__(self, login, fullname):
    self.uuid = str(uuid.uuid4())

    self.fullname = fullname
    self.intra_uid = login

    if '@' in login:
      self.username = slugify(login.split('@')[0])
      self.realm = login.split('@')[1]
    else:
      self.username = slugify(login)
      self.realm = 'legacy'

    count = 1
    username = self.username
    while User.query.filter_by(username=self.username).first():
      count += 1
      self.username = username + str(count)

  def register(self, office365_uid, email, firstname, lastname):
    self.registered = True

    self.office365_uid = office365_uid

    self.rtime = db.func.current_timestamp()
    self.email = email
    self.firstname = firstname
    self.lastname = lastname
    self.fullname = firstname + ' ' + lastname

  def unregister(self):
    self.registered = False
    self.office365_uid = None
    self._office365_token = None
    self.intra_token = None
    self.rtime = None
    self.email = None
    self.public = False

    # delete data
    for info in self.custom_infos:
      db.session.delete(info)
    if self.academic is not None:
      db.session.delete(self.academic)
    for app in self.oauth_apps:
      db.session.delete(app)
    for token in self.oauth_tokens:
      db.session.delete(token)
    db.session.commit()

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


#
# Custom profile infos types
#
class UserProfileCustomInfoTypes(Enum):
  country = auto()
  city = auto()
  address = auto()
  job = auto()
  phone = auto()
  birthday = auto()
  birthplace = auto()
  twitter = auto()
  website = auto()
  email = auto()
  googleplus = auto()
  facebook = auto()
  discord = auto()
  linkedin = auto()
  github = auto()


#
# User custom profile infos
#
class UserProfileCustomInfo(Intra):

  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  type = db.Column(db.Enum(UserProfileCustomInfoTypes), nullable=False)

  value = db.Column(db.String(255), nullable=False)
  public = db.Column(db.Boolean, nullable=False, default=True)

  def __init__(self, user, type, value):
    self.user_id = user.id
    self.type = type

    self.value = value

  def __repr__(self):
    return '<UserProfileCustomInfo %r>' % self.id


#
# Groups
#
class UserGroup(Intra):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)
  intra_code = db.Column(db.String(255), index=True, unique=True, nullable=False)

  # group info
  # member count represents number of members on intra-side, not on extranet's side
  name = db.Column(db.String(255), nullable=False)
  description = db.Column(db.Text)
  member_count = db.Column(db.Integer, nullable=False)

  # group manager
  manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

  def __init__(self, code, name, description, count, manager):
    self.uuid = str(uuid.uuid4())
    self.intra_code = code

    self.name = name
    self.description = description
    self.member_count = count

    self.manager_id = manager.id

  def __repr__(self):
    return '<UserGroup %r>' % self.id


#
# User academic data
#
class UserAcademic(Intra):

  # owner
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

  # school
  school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
  school = db.relationship('School', lazy=True, backref=db.backref('user_academics', lazy=True))
  school_year = db.Column(db.Integer, nullable=False)

  # current status
  promotion_id = db.Column(db.Integer, db.ForeignKey('promotion.id'), nullable=False)
  promotion = db.relationship('Promotion', lazy=True, backref=db.backref('user_academics', lazy=True))
  course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
  course = db.relationship('Course', lazy=True, backref=db.backref('user_academics', lazy=True))
  semester = db.Column(db.Integer, nullable=False)
  year_of_study = db.Column(db.Integer, nullable=False)

  # location
  country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
  country = db.relationship('Country', lazy=True, backref=db.backref('user_academics', lazy=True))
  city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
  city = db.relationship('City', lazy=True, backref=db.backref('user_academics', lazy=True))

  # user performance
  credits = db.Column(db.Integer, nullable=False)
  gpa = db.Column(db.Integer, nullable=False)
  spice_available = db.Column(db.Integer, nullable=False)
  spice_consumed = db.Column(db.Integer, nullable=False)
  netsoul_active = db.Column(db.Integer, nullable=False)
  netsoul_norm = db.Column(db.Integer, nullable=False)

  def __init__(self, user):
    self.user_id = user.id

  def __repr__(self):
    return '<UserAcademic %r>' % self.id