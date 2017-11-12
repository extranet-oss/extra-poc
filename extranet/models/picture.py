import uuid
import json
import os
from PIL import Image
from flask import url_for
from sqlalchemy import event

from extranet import app, db
from extranet.models._templates import Base

#
# picture settings
#
PICTURE_STATIC_DIR = 'picture/'
PICTURE_DIR = app.static_folder + '/' + PICTURE_STATIC_DIR
FORMAT = 'jpg'
FORMAT_SETTINGS = {
  'progressive': True,
  'quality': 95
}
SIZES = [
  (32, 32),
  (64, 64),
  (128, 128),
  (256, 256),
  (512, 512)
]


#
# used to save a new picture, its thumbnails included
#
def save_picture(uuid, image):
  os.makedirs(PICTURE_DIR, exist_ok=True)

  # save original image
  image = image.convert('RGB')
  image.save(PICTURE_DIR + uuid + '.' + FORMAT,
             **FORMAT_SETTINGS)

  # save thumbnails
  for size in SIZES:
    os.makedirs(PICTURE_DIR + str(size[0]) + 'x' + str(size[1]) + '/', exist_ok=True)

    # calculate crop box
    box = None
    box_size = (
      size[0] * image.height / size[1],
      size[1] * image.width / size[0]
    )
    if box_size[0] < image.width:
      box = (
        image.width / 2 - box_size[0] / 2,
        0,
        image.width / 2 - box_size[0] / 2 + box_size[0],
        image.height
      )
    elif box_size[1] < image.height:
      box = (
        0,
        image.height / 2 - box_size[1] / 2,
        image.width,
        image.height / 2 - box_size[1] / 2 + box_size[1]
      )

    # crop, resize & save
    resized = image.resize(size, Image.BICUBIC, box)
    resized.save(PICTURE_DIR + str(size[0]) + 'x' + str(size[1]) + '/' + uuid + '.' + FORMAT,
                 **FORMAT_SETTINGS)


#
# picture model
#
class Picture(Base):

  # uuid
  uuid = db.Column(db.String(36), index=True, unique=True, nullable=False)

  # picture metadata
  # origin can be:
  # - intra:<url>
  # - upload
  origin = db.Column(db.String(255), index=True, nullable=False)
  width = db.Column(db.Integer, nullable=False)
  height = db.Column(db.Integer, nullable=False)
  checksum = db.Column(db.String(32))

  # available sizes
  _sizes = db.Column(db.Text, name='sizes', nullable=False)

  def __init__(self, image, origin='upload'):
    self.uuid = str(uuid.uuid4())

    self.origin = origin
    self.width = image.width
    self.height = image.height

    self.sizes = SIZES

    save_picture(self.uuid, image)

  @property
  def sizes(self):
    return json.loads(self._sizes)

  @sizes.setter
  def sizes(self, value):
    self._sizes = json.dumps(value)

  def get_url(self, size=None):
    subdir = ''
    if size is not None and [size[0], size[1]] in self.sizes:
      subdir = str(size[0]) + 'x' + str(size[1]) + '/'

    return url_for('static', filename=PICTURE_STATIC_DIR + subdir + self.uuid + '.' + FORMAT)

  @property
  def url(self):
    return self.get_url()

  def __repr__(self):
    return '<Picture %r>' % self.id


#
# Called when a picture gets deleted
#
@event.listens_for(Picture, 'before_delete')
def before_delete_event(mapper, connection, target):
  filename = PICTURE_DIR + target.uuid + '.' + FORMAT

  # delete original picture
  if os.path.exists(filename):
    os.remove(filename)

  # delete all thumbnails
  for size in target.sizes:
    filename = PICTURE_DIR + str(size[0]) + 'x' + str(size[1]) + '/' + target.uuid + '.' + FORMAT

    if os.path.exists(filename):
      os.remove(filename)