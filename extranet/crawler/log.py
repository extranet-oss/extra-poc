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