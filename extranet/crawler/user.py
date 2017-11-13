import traceback

from extranet import app, db
from extranet.connections.intranet import client, IntranetInvalidToken
from extranet.crawler.log import new_log, needs_crawling
from extranet.crawler import group
from extranet.models.user import UserProfileCustomInfoTypes, UserProfileCustomInfo, UserGroup, UserAcademic
from extranet.models.school import School, Promotion, Course
from extranet.models.location import Country, City

CUSTOM_INFOS = {
  'job': UserProfileCustomInfoTypes.job,
  'city': UserProfileCustomInfoTypes.city,
  'telephone': UserProfileCustomInfoTypes.phone,
  'country': UserProfileCustomInfoTypes.country,
  'address': UserProfileCustomInfoTypes.address,
  'twitter': UserProfileCustomInfoTypes.twitter,
  'email': UserProfileCustomInfoTypes.email,
  'website': UserProfileCustomInfoTypes.website,
  'googleplus': UserProfileCustomInfoTypes.googleplus,
  'facebook': UserProfileCustomInfoTypes.facebook,
  'poste': UserProfileCustomInfoTypes.job,
  'birthday': UserProfileCustomInfoTypes.birthday,
  'birthplace': UserProfileCustomInfoTypes.birthplace,
}

def update(user):

  # Quit if user has no autologin registered
  if user.intra_token is None:
    return

  # Quit if user data is recent enough
  log_key = 'user:' + user.uuid
  if not needs_crawling(log_key):
    return

  # Create a log to track crawling status
  log = new_log(log_key)

  # First load data from intranet
  try:
    print('Loading user data...')
    user_data = client.get_user(token=user.intra_token)
  except IntranetInvalidToken:
    user.intra_token = None
    user.intra_token_expired = True
    db.session.add(user)
    db.session.commit()
    log.fail('Failed to load ressource:\n' + traceback.format_exc())
    print(log.msg)
    return
  except:
    log.fail('Failed to load ressource:\n' + traceback.format_exc())
    print(log.msg)
    return

  # process main user data
  try:
    print('Processing user data...')

    # update timestamps
    user.ctime = user_data['ctime']
    user.mtime = user_data['mtime']

    # delete old custom info
    for custom_info in user.custom_infos:
      for key, value in CUSTOM_INFOS.items():
        if value == custom_info.type:
          if key not in user_data['userinfo']:
            db.session.delete(custom_info)
            print('Deleted user custom info')
          break

    # add/update custom info
    for key, info in user_data['userinfo'].items():
      info_entry = UserProfileCustomInfo.query.filter_by(type=CUSTOM_INFOS[key], user=user).first()
      if info_entry is None:
        info_entry = UserProfileCustomInfo(user, CUSTOM_INFOS[key], info['value'])
        user.custom_infos.append(info_entry)
        print('Created user custom info')
      else:
        info_entry.value = info['value']
        print('Updated user custom info')

      info_entry.public = info['public'] if 'public' in info else False

    # setup user academic profile
    if user.academic is None:
      user.academic = UserAcademic(user)
      print("Created user academic profile")

    # academic profile update
    # no_autoflush, because queries here flush and we don't want this
    with db.session.no_autoflush:
      school = School.query.filter_by(intra_code=user_data['school_code']).first()
      if school is None:
        school = School(user_data['school_code'], user_data['school_title'])
      user.academic.school = school
      user.academic.school_year = int(user_data['scolaryear'])

      promotion = Promotion.query.filter_by(intra_code=str(user_data['promo'])).first()
      if promotion is None:
        promotion = Promotion(str(user_data['promo']), str(user_data['promo']))
      user.academic.promotion = promotion

      course = Course.query.filter_by(intra_code=user_data['course_code']).first()
      if course is None:
        course = Course(user_data['course_code'], user_data['course_code'])
      user.academic.course = course

      user.academic.semester = user_data['semester']
      user.academic.year_of_study = user_data['studentyear']

      user.academic.country = Country.query.filter_by(intra_code=user_data['location'][:2]).first()
      user.academic.city = City.query.filter_by(intra_code=user_data['location']).first()

      user.academic.credits = user_data['credits']
      try:
        user.academic.gpa = int(float(user_data['gpa'][0]['gpa']) * 100)
      except ValueError:
        user.academic.gpa = 0
      # we're not supporting this for now.
      # intranet is too autistic, i need to calculate those values on my own
      # so i need to be able to crawl modules, spices, etc
      user.academic.spice_available = 0
      user.academic.spice_consumed = 0
      user.academic.netsoul_active = 0
      user.academic.netsoul_norm = 0

    db.session.add(user)
    db.session.commit()
  except:
    db.session.rollback()
    log.fail('Failed to process data:\n' + traceback.format_exc())
    print(log.msg)
    return

  # process user groups
  # we're not setting member status here, subcrawl will do it for us
  groups = []
  try:
    print('Processing user data...')
    for group_data in user_data['groups']:
      group_entry = UserGroup.query.filter_by(intra_code=group_data['name']).first()
      if group_entry is None:
        group_entry = UserGroup(group_data['name'], group_data['title'], group_data['count'])
      groups.append(group_entry)
      db.session.add(group_entry)
    db.session.commit()
  except:
    db.session.rollback()
    log.fail('Failed to process data:\n' + traceback.format_exc())
    print(log.msg)
    return

  # Everything is OK, save log status
  log.ok()
  print(log.msg)

  # start subcrawls
  for group_entry in groups:
    group.update(group_entry)