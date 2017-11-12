import traceback
from sqlalchemy import not_
from hashlib import md5

from extranet import app, db
from extranet.connections.intranet import client, IntranetNotFound, IntranetInvalidResponse
from extranet.crawler.log import new_log, needs_crawling
from extranet.models.user import User
from extranet.models.picture import Picture

def update():

  # Quit if data is recent enough
  log_key = 'all_users'
  if not needs_crawling(log_key):
    return

  # Create a log to track crawling status
  log = new_log(log_key)

  # First load data from intranet
  try:
    print('Loading user data...')
    data = client.get_all_users(token=app.config['CRAWLER_DEFAULT_TOKEN'])
  except:
    log.fail('Failed to load ressource:\n' + traceback.format_exc())
    print(log.msg)
    return

  # Then process user data
  #user_ids = []
  try:
    print('Processing users data...')

    for user_data in data:

      # abort if entry isn't a user, just in case
      if user_data['type'] != 'user':
        continue

      # get user, or create it if needed
      user = User.query.filter_by(intra_uid=user_data['login']).first()
      fullname = user_data['title'] if 'title' in user_data else user_data['login']
      if user is None:
        user = User(user_data['login'], fullname)
        print('Created user', user_data['login'])

      # try to get user picture
      try:
        picture_data = client.get_picture(user_data['login'])
      except IntranetNotFound:
        print('Picture not found. skipping')
      except IntranetInvalidResponse:
        print('Picture invalid. skipping')
      except:
        print('Failed to get user picture')
        raise

      # we successfully got user picture, process it
      else:
        # Calculate checksum & compare it to saved user picture if applicable
        checksum = md5(picture_data.tobytes()).hexdigest()
        save_new_picture = True if user.picture is None else False
        if user.picture is not None and checksum != user.picture.checksum:
          db.session.delete(user.picture)
          save_new_picture = True
          print('Deleted outdated user picture')

        # user picture is outdated, save it
        if save_new_picture:
          user.picture = Picture(picture_data, 'intra:' + user.uuid)
          user.picture.checksum = checksum
          print('Created user picture')

      # save changes
      db.session.add(user)
      db.session.commit()

      #user_ids.append(user.id)
  except:
    db.session.rollback()
    log.fail('Failed to process data:\n' + traceback.format_exc())
    print(log.msg)
    return

  # Delete old users
  # ---
  # On second tought, i might not do this, in case they destroy the magic endpoint
  # i'm using to get all users in a row. This scenario might destroy my database in
  # a few seconds!!!!
  #
  #try:
  #  print('Deleting old users...')
  #  for row in User.query.filter(not_(User.id.in_(user_ids))).all():
  #    db.session.delete(row)
  #  db.session.commit()
  #except:
  #  db.session.rollback()
  #  log.fail('Failed to delete outdated data:\n' + traceback.format_exc())
  #  print(log.msg)
  #  return

  # Everything is OK, save log status
  log.ok()
  print(log.msg)