import uuid
import json
from enum import Enum, auto

from extranet import db
from extranet.models._templates import Dated, Intra

user_groups = db.Table('user_xref_user_group',
  db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
  db.Column('user_group_id', db.Integer, db.ForeignKey('user_group.id'), primary_key=True)
)


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

  # relations
  profile = db.relationship('UserProfile', lazy=True, backref=db.backref('user', lazy=True), cascade='all, delete-orphan', uselist=False)
  groups = db.relationship('UserGroup', secondary=user_groups, lazy=True, backref=db.backref('users', lazy=True))
  managed_groups = db.relationship('UserGroup', lazy=True, backref=db.backref('master', lazy=True))
  academic = db.relationship('UserAcademic', lazy=True, backref=db.backref('user', lazy=True), cascade='all, delete-orphan', uselist=False)
  oauth_apps = db.relationship('OauthApp', lazy=True, backref=db.backref('owner', lazy=True), cascade='all, delete-orphan')
  oauth_tokens = db.relationship('OauthToken', lazy=True, backref=db.backref('user', lazy=True), cascade='all, delete-orphan')

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


class UserProfile(Intra):

  # owner
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

  # timestamps
  ctime = db.Column(db.DateTime, nullable=False)
  mtime = db.Column(db.DateTime, nullable=False)

  # profile access (public means profile accessible to everyone, findable on userlist)
  public = db.Column(db.Boolean, nullable=False, default=False)

  # profile pic
  picture_id = db.Column(db.Integer, db.ForeignKey('picture.id'))
  picture = db.relationship('Picture', lazy=True, backref=db.backref('user', lazy=True), cascade='all, delete-orphan', single_parent=True)

  # custom user info
  custom_infos = db.relationship('UserProfileCustomInfo', lazy=True, backref=db.backref('user_profile', lazy=True), cascade='all, delete-orphan')

  def __init__(self, user, ctime, mtime):
    self.user_id = user.id

    self.ctime = ctime
    self.mtime = mtime

  def __repr__(self):
    return '<UserProfile %r>' % self.id


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


class UserProfileCustomInfo(Intra):

  user_profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)
  type = db.Column(db.Enum(UserProfileCustomInfoTypes), nullable=False)

  value = db.Column(db.String(255), nullable=False)
  public = db.Column(db.Boolean, nullable=False, default=True)

  def __init__(self, user_profile, type, value):
    self.user_profile_id = user_profile.id
    self.type = type

    self.value = value

  def __repr__(self):
    return '<UserProfileCustomInfo %r>' % self.id


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
  manager_intra_uid = db.Column(db.String(320), nullable=False)
  manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __init__(self, code, name, description, count, manager_login):
    self.uuid = uuid.uuid4()
    self.intra_code = code

    self.name = name
    self.description = description
    self.member_count = count

    self.manager_intra_uid = manager_login

  def __repr__(self):
    return '<UserGroup %r>' % self.id


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