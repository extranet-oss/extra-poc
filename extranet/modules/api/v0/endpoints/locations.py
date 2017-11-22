from extranet.modules.api.v0 import api
from extranet.models.location import City

@api.get('/cities/')
def get_cities():
    cities = []
    for city in City.query:
        cities.append({
            'uuid': city.uuid,
            'name': city.name
        })

    return {
        'data': cities,
        'links': {
            'self': api.url_for('get_cities')
        }
    }
