import traceback
from sqlalchemy import not_

from extranet import app, db
from extranet.crawler import api
from extranet.crawler.log import new_log, needs_crawling
from extranet.models.location import Country, City, Building, Room, RoomType

def update():

  # Quit if locations are recent enough
  log_key = 'locations'
  if not needs_crawling(log_key):
    return

  # Create a log to track crawling status
  log = new_log(log_key)

  #
  # So how do we proceed here,
  # we get data from intranet, it should be parsed by the api wrapper
  # then we generate a tree of locations, to sort it by country, city then buildings
  # then we crawl that tree ignoring disabled branches, creating/updating entities on the fly
  # also each entry of the tree gets processed to extract associated room if applicable
  #

  # First load data from intranet
  try:
    print('Loading locations ressource...')
    api.set_custom_token(app.config['CRAWLER_DEFAULT_TOKEN'])
    locations = api.locations()
  except:
    log.fail('Failed to load ressource:\n' + traceback.format_exc())
    print(log.msg)
    return

  # used to track what we added/updated, to delete uneeded data after
  country_instances = []
  city_instances = []
  building_instances = []
  room_instances = []
  room_type_instances = []

  # Next we process the damn data
  try:
    # We need to create a tree to sort locations
    # -> country
    #   -> city
    #     -> building
    #       -> room
    print('Creating location tree...')
    tree = {}
    for code, location in locations.items():
      path = code.split('/')

      # create country
      if len(path) >= 1 and path[0] not in tree:
        tree[path[0]] = {}

      # create city
      if len(path) >= 2 and path[1] not in tree[path[0]]:
        tree[path[0]][path[1]] = {}

      # create building
      if len(path) >= 3 and path[2] not in tree[path[0]][path[1]]:
        tree[path[0]][path[1]][path[2]] = []

      # add room
      if len(path) >= 4 and path[3] not in tree[path[0]][path[1]][path[2]]:
        tree[path[0]][path[1]][path[2]].append(path[3])

    # This functions checks if a location is a room (country, city, building can be a room, why not)
    # if it is, the corresponding room is added with its room type
    def process_rooms(location, key, country=None, city=None, building=None, room=None):
      if 'types' not in location:
        return

      types = []
      seats = 0

      # we first get associated room types
      for room in location['types']:

        # Create or update associated room type
        type_entry = RoomType.query.filter_by(intra_code=room['type']).first()
        if not type_entry:
          type_entry = RoomType(room['type'], room['title'])
          print('Created room type', room['type'])
        else:
          type_entry.title = room['title']
          print('Updated room type', room['type'])
        db.session.add(type_entry)
        room_type_instances.append(type_entry)

        # Update seats (keep highest, we don't care, it's the same room anyways)
        if room['seats'] > seats:
          seats = room['seats']

        # save type
        types.append(type_entry)

      # Create or update room
      room_entry = Room.query.filter_by(intra_code=key).first()
      if not room_entry:
        room_entry = Room(key, location['title'], seats, types, country, city, building)
        print('Created room', key)
      else:
        room_entry.title = location['title']
        room_entry.seats = seats
        room_entry.types = types
        print('Updated room', key)
      db.session.add(room_entry)
      room_instances.append(room_entry)

    # After we need to process the tree
    # We ignore disabled branches to keep our database clean
    # Corresponding location key is generated according to item codes
    print('Processing tree...')
    for country, cities in tree.items():
      key = country
      if 'disabled' in locations[key] and locations[key]['disabled']:
        continue

      # Create or update country
      country_entry = Country.query.filter_by(intra_code=key).first()
      if not country_entry:
        country_entry = Country(key, locations[key]['title'])
        print('Created country', key)
      else:
        country_entry.title = locations[key]['title']
        print('Updated country', key)
      db.session.add(country_entry)
      country_instances.append(country_entry)

      # process country rooms if applicable
      process_rooms(locations[key], key, country_entry)

      for city, buildings in cities.items():
        key = country + '/' + city
        if 'disabled' in locations[key] and locations[key]['disabled']:
          continue

        # Create or update city
        city_entry = City.query.filter_by(intra_code=key, country=country_entry).first()
        if not city_entry:
          city_entry = City(key, locations[key]['title'], country_entry)
          print('Created city', key)
        else:
          city_entry.title = locations[key]['title']
          print('Updated city', key)
        db.session.add(city_entry)
        city_instances.append(city_entry)

        # process city rooms if applicable
        process_rooms(locations[key], key, country_entry, city_entry)

        for building, rooms in buildings.items():
          key = country + '/' + city + '/' + building
          if 'disabled' in locations[key] and locations[key]['disabled']:
            continue

          # Create or update building
          building_entry = Building.query.filter_by(intra_code=key, city=city_entry).first()
          if not building_entry:
            building_entry = Building(key, locations[key]['title'], country_entry, city_entry)
            print('Created building', key)
          else:
            building_entry.title = locations[key]['title']
            print('Updated building', key)
          db.session.add(building_entry)
          building_instances.append(building_entry)

          # Process building rooms if applicable
          process_rooms(locations[key], key, country_entry, city_entry, building_entry)

          for room in rooms:
            key = country + '/' + city + '/' + building + '/' + room
            if 'disabled' in locations[key] and locations[key]['disabled']:
              continue

            # Process this room
            process_rooms(locations[key], key, country_entry, city_entry, building_entry)

    db.session.commit()
  except:
    db.session.rollback()
    log.fail('Failed to process data:\n' + traceback.format_exc())
    print(log.msg)
    return

  # We now need to delete unused data (eg. a location was deleted)
  try:
    print('Deleting old locations...')
    for row in Room.query.filter(not_(Room.id.in_([e.id for e in room_instances]))).all():
      db.session.delete(row)
    for row in RoomType.query.filter(not_(RoomType.id.in_([e.id for e in room_type_instances]))).all():
      db.session.delete(row)
    for row in Building.query.filter(not_(Building.id.in_([e.id for e in building_instances]))).all():
      db.session.delete(row)
    for row in City.query.filter(not_(City.id.in_([e.id for e in city_instances]))).all():
      db.session.delete(row)
    for row in Country.query.filter(not_(Country.id.in_([e.id for e in country_instances]))).all():
      db.session.delete(row)

    db.session.commit()
  except:
    db.session.rollback()
    log.fail('Failed to delete outdated data:\n' + traceback.format_exc())
    print(log.msg)
    return

  # Everything is OK, save log status
  log.ok()
  print(log.msg)