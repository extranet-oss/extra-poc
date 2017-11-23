from extranet.modules.api.v0 import api
from extranet.models.location import Country, City, Building, Room
from extranet.modules.api.v0.schemas.locations import CountrySchema, CitySchema, BuildingSchema, RoomSchema

@api.get('/locations/countries/')
def list_countries():
    countries = Country.query.all()

    result = CountrySchema().dump(countries, many=True)
    return result.data

@api.get('/locations/countries/<identifier>/')
def get_country(identifier):
    country = Country.query.filter_by(uuid=identifier).first()

    result = CountrySchema().dump(country)
    return result.data

@api.get('/locations/countries/<identifier>/cities/')
def get_country_cities(identifier):
    country = Country.query.filter_by(uuid=identifier).first()

    result = CitySchema().dump(country.cities, many=True)
    return result.data

@api.get('/locations/countries/<identifier>/buildings/')
def get_country_buildings(identifier):
    country = Country.query.filter_by(uuid=identifier).first()

    result = BuildingSchema().dump(country.buildings, many=True)
    return result.data

@api.get('/locations/countries/<identifier>/rooms/')
def get_country_rooms(identifier):
    country = Country.query.filter_by(uuid=identifier).first()

    result = RoomSchema().dump(country.rooms, many=True)
    return result.data


@api.get('/locations/cities/')
def list_cities():
    cities = City.query.all()

    result = CitySchema().dump(cities, many=True)
    return result.data

@api.get('/locations/cities/<identifier>/')
def get_city(identifier):
    city = City.query.filter_by(uuid=identifier).first()

    result = CitySchema().dump(city)
    return result.data

@api.get('/locations/cities/<identifier>/buildings/')
def get_city_buildings(identifier):
    city = City.query.filter_by(uuid=identifier).first()

    result = BuildingSchema().dump(city.buildings, many=True)
    return result.data

@api.get('/locations/cities/<identifier>/rooms/')
def get_city_rooms(identifier):
    city = City.query.filter_by(uuid=identifier).first()

    result = RoomSchema().dump(city.rooms, many=True)
    return result.data


@api.get('/locations/buildings/')
def list_buildings():
    buildings = Building.query.all()

    result = BuildingSchema().dump(buildings, many=True)
    return result.data

@api.get('/locations/buildings/<identifier>/')
def get_building(identifier):
    building = Building.query.filter_by(uuid=identifier).first()

    result = BuildingSchema().dump(building)
    return result.data

@api.get('/locations/buildings/<identifier>/rooms/')
def get_building_rooms(identifier):
    building = Building.query.filter_by(uuid=identifier).first()

    result = RoomSchema().dump(building.rooms, many=True)
    return result.data


@api.get('/locations/rooms/')
def list_rooms():
    rooms = Room.query.all()

    result = RoomSchema().dump(rooms, many=True)
    return result.data

@api.get('/locations/rooms/<identifier>/')
def get_room(identifier):
    room = Room.query.filter_by(uuid=identifier).first()

    result = RoomSchema().dump(room)
    return result.data
