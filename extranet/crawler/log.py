import datetime

from extranet import db
from extranet.models.crawler import CrawlerLog

class CrawlerLogHelper():

  def __init__(self, type):
    self.log = CrawlerLog(type)
    db.session.add(self.log)
    db.session.commit()
    self.update()

  def fail(self, msg='FAILED'):
    self.log.status = 0
    self.log.msg = msg
    db.session.add(self.log)
    db.session.commit()
    self.update()

  def ok(self, msg='OK'):
    self.log.status = 1
    self.log.msg = msg
    db.session.add(self.log)
    db.session.commit()
    self.update()

  def update(self):
    self.status = self.log.status
    self.msg = self.log.msg

def new_log(type):
  return CrawlerLogHelper(type)

maxages = {
  'default': 60
}

# How do we determine if a given ressource type should not be crawled:
# - if the latest succeeded log is recent enough, ignoring failed logs
# - if the latest log represents a wip crawling procedure
def needs_crawling(type):
  latest = CrawlerLog.query
           .filter_by(type=type)
           .filter(CrawlerLog.status != 0)
           .order_by(CrawlerLog.time.desc())
           .first()

  # No crawler logs found, needs to be crawled
  if latest is None:
    return True

  # Latest crawler log tells us the ressource is being updated, do not interfere pls
  if latest.status == -1:
    return False

  delta = datetime.datetime.utcnow() - latest.time
  maxage = maxages[type] if type in maxages else maxages['default']

  # if crawler log is too old, update
  if delta > datetime.timedelta(seconds=maxage):
    return True

  return False