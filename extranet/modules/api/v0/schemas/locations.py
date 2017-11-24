from marshmallow_jsonapi import fields

from extranet.modules.api.v0.api.marshmallow import Relationship, Schema

class CountrySchema(Schema):
    id = fields.Str(attribute="uuid", dump_only=True)
    slug = fields.Str()
    name = fields.Str()

    child_cities = Relationship(
        attribute="cities",
        related_view='get_country_cities',
        related_view_kwargs={'identifier': '<uuid>'},
        many=True,
        include_resource_linkage=True,
        type_='city',
        schema='CitySchema',
        id_field='uuid',
        default=None
    )

    child_buildings = Relationship(
        attribute="buildings",
        related_view='get_country_buildings',
        related_view_kwargs={'identifier': '<uuid>'},
        many=True,
        include_resource_linkage=True,
        type_='building',
        schema='BuildingSchema',
        id_field='uuid',
        default=None
    )

    child_rooms = Relationship(
        attribute="rooms",
        related_view='get_country_rooms',
        related_view_kwargs={'identifier': '<uuid>'},
        many=True,
        include_resource_linkage=True,
        type_='room',
        schema='RoomSchema',
        id_field='uuid',
        default=None
    )

    class Meta:
        type_ = 'country'
        self_view = 'get_country'
        self_view_kwargs = {'identifier': '<id>'}
        self_view_many = 'list_countries'
        strict = True


class CitySchema(Schema):
    id = fields.Str(attribute="uuid", dump_only=True)
    slug = fields.Str()
    name = fields.Str()

    parent_country = Relationship(
        attribute="country",
        related_view='get_country',
        related_view_kwargs={'identifier': '<country.uuid>'},
        include_resource_linkage=True,
        type_='country',
        schema='CountrySchema',
        id_field='uuid',
        default=None
    )

    child_buildings = Relationship(
        attribute="buildings",
        related_view='get_city_buildings',
        related_view_kwargs={'identifier': '<uuid>'},
        many=True,
        include_resource_linkage=True,
        type_='building',
        schema='BuildingSchema',
        id_field='uuid',
        default=None
    )

    child_rooms = Relationship(
        attribute="rooms",
        related_view='get_city_rooms',
        related_view_kwargs={'identifier': '<uuid>'},
        many=True,
        include_resource_linkage=True,
        type_='room',
        schema='RoomSchema',
        id_field='uuid',
        default=None
    )

    class Meta:
        type_ = 'city'
        self_view = 'get_city'
        self_view_kwargs = {'identifier': '<id>'}
        self_view_many = 'list_cities'
        strict = True


class BuildingSchema(Schema):
    id = fields.Str(attribute="uuid", dump_only=True)
    slug = fields.Str()
    name = fields.Str()

    parent_country = Relationship(
        attribute="country",
        related_view='get_country',
        related_view_kwargs={'identifier': '<country.uuid>'},
        include_resource_linkage=True,
        type_='country',
        schema='CountrySchema',
        id_field='uuid',
        default=None
    )

    parent_city = Relationship(
        attribute="city",
        related_view='get_city',
        related_view_kwargs={'identifier': '<city.uuid>'},
        include_resource_linkage=True,
        type_='city',
        schema='CitySchema',
        id_field='uuid',
        default=None
    )

    child_rooms = Relationship(
        attribute="rooms",
        related_view='get_building_rooms',
        related_view_kwargs={'identifier': '<uuid>'},
        many=True,
        include_resource_linkage=True,
        type_='room',
        schema='RoomSchema',
        id_field='uuid',
        default=None
    )

    class Meta:
        type_ = 'building'
        self_view = 'get_building'
        self_view_kwargs = {'identifier': '<id>'}
        self_view_many = 'list_buildings'
        strict = True


class RoomSchema(Schema):
    id = fields.Str(attribute="uuid", dump_only=True)
    slug = fields.Str()
    name = fields.Str()

    parent_country = Relationship(
        attribute="country",
        related_view='get_country',
        related_view_kwargs={'identifier': '<country.uuid>'},
        include_resource_linkage=True,
        type_='country',
        schema='CountrySchema',
        id_field='uuid',
        default=None
    )

    parent_city = Relationship(
        attribute="city",
        related_view='get_city',
        related_view_kwargs={'identifier': '<city.uuid>'},
        include_resource_linkage=True,
        type_='city',
        schema='CitySchema',
        id_field='uuid',
        default=None
    )

    parent_building = Relationship(
        attribute="building",
        related_view='get_building',
        related_view_kwargs={'identifier': '<building.uuid>'},
        include_resource_linkage=True,
        type_='building',
        schema='BuildingSchema',
        id_field='uuid',
        default=None
    )

    class Meta:
        type_ = 'room'
        self_view = 'get_room'
        self_view_kwargs = {'identifier': '<id>'}
        self_view_many = 'list_rooms'
        strict = True
