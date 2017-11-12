import traceback
from sqlalchemy import not_

from extranet import app, db
from extranet.connections.intranet import client
from extranet.crawler.log import new_log, needs_crawling
from extranet.models.user import User, UserGroup

def update(group):

  # Quit if grou data is recent enough
  log_key = 'group:' + group.uuid
  if not needs_crawling(log_key):
    return

  # Create a log to track crawling status
  log = new_log(log_key)

  # First load data from intranet
  try:
    print('Loading group ressource...')
    group_data = client.get_group(group.intra_code, token=app.config['CRAWLER_DEFAULT_TOKEN'])
    group_members = client.get_group_members(group.intra_code, token=app.config['CRAWLER_DEFAULT_TOKEN'])
  except:
    log.fail('Failed to load ressource:\n' + traceback.format_exc())
    print(log.msg)
    return

  # process data
  members = []
  try:
    print('Processing data')

    # update basic data
    group.name = group_data['title']
    group.description = group_data['description']
    group.member_count = group_data['count']

    # update manager
    if 'master' in group_data:
      group.manager = User.query.filter_by(intra_uid=group_data['master']['login']).first()
    else:
      group.manager = None

    # update members
    for member in group_members:
      if member['type'] == 'user':
        user = User.query.filter_by(intra_uid=member['login']).first()
        if user not in group.members:
          group.members.append(user)
        members.append(user.id)

      if member['type'] == 'group':
        subgroup = UserGroup.query.filter_by(intra_code=member['login']).first()
        if subgroup is None:
          subgroup = UserGroup(member['login'], member['title'], 0)
        subgroup.parent = group

    db.session.add(group)
    db.session.commit()
  except:
    db.session.rollback()
    log.fail('Failed to process data:\n' + traceback.format_exc())
    print(log.msg)
    return

  # Clean group members
  try:
    print('Deleting old members...')
    for member in group.members.copy():
      if member.id not in members:
        group.members.discard(user)

    db.session.add(group)
    db.session.commit()
  except:
    db.session.rollback()
    log.fail('Failed to delete outdated data:\n' + traceback.format_exc())
    print(log.msg)
    return

  # Everything is OK, save log status
  log.ok()
  print(log.msg)

  # start subcrawls
  for subgroup in group.children:
    update(subgroup)