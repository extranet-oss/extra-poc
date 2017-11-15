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


# maxages values are for testing, it is not optimized
maxages = {
    'default': 60,                        # 1 minute
    'locations': 60 * 60 * 24 * 31 * 12,  # 1 year
    'all_users': 60 * 60 * 24 * 31 * 6,   # 6 months
    'user': 60 * 60,                      # 1 hour
    'group': 60 * 60 * 24 * 31            # 1 month
}


# How do we determine if a given ressource type should not be crawled:
# - if the latest succeeded log is recent enough, ignoring failed logs
# - if the latest log represents a wip crawling procedure
def needs_crawling(type):
    latest = CrawlerLog.query.filter_by(type=type).filter(CrawlerLog.status != 0).order_by(CrawlerLog.time.desc()).first()

    # No crawler logs found, needs to be crawled
    if latest is None:
        return True

    # Latest crawler log tells us the ressource is being updated, do not interfere pls
    if latest.status == -1:
        return False

    delta = datetime.datetime.utcnow() - latest.time
    key = type.split(':')[0]
    maxage = maxages[key] if key in maxages else maxages['default']

    # if crawler log is too old, update
    if delta > datetime.timedelta(seconds=maxage):
        return True

    return False
