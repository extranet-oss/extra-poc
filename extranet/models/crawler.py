from extranet import db
from extranet.models._templates import Base

class CrawlerLog(Base):

  type = db.Column(db.String(255), index=True, nullable=False)
  time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(),
                                                onupdate=db.func.current_timestamp())
  status = db.Column(db.Integer, nullable=False) # -1=working, 0=failed, 1=succeeded
  msg = db.Column(db.Text)

  def __init__(self, type, msg=None):
    self.type = type
    self.status = -1
    self.msg = msg

  def __repr__(self):
    return '<CrawlerLog %r>' % self.id