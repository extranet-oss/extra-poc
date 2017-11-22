from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

class CountrySchema(Schema):
    id = fields.Str(attribute="uuid", dump_only=True)
    slug = fields.Str()
    name = fields.Str()

    class Meta:
        type_ = 'country'
        self_view = '.get_country'
        self_view_kwargs = {'identifier': '<id>'}
        self_view_many = '.list_countries'
        strict = True


class CitySchema(Schema):
    id = fields.Str(attribute="uuid", dump_only=True)
    slug = fields.Str()
    name = fields.Str()

    country = Relationship(
        #self_view='.get_country',
        #self_url_kwargs={'identifier': '<id>'},
        related_view='.get_country',
        related_view_kwargs={'identifier': '<country.uuid>'},
        type_='country',
        schema='CountrySchema',
        id_field='uuid',
        default=None
    )

    class Meta:
        type_ = 'city'
        self_view = '.get_city'
        self_view_kwargs = {'identifier': '<id>'}
        self_view_many = '.list_cities'
        strict = True


class BuildingSchema(Schema):
    id = fields.Str(attribute="uuid", dump_only=True)
    slug = fields.Str()
    name = fields.Str()

    country = Relationship(
        #self_view='.get_country',
        #self_url_kwargs={'identifier': '<id>'},
        related_view='.get_country',
        related_view_kwargs={'identifier': '<country.uuid>'},
        type_='country',
        schema='CountrySchema',
        id_field='uuid',
        default=None
    )

    city = Relationship(
        #self_view='.get_city',
        #self_url_kwargs={'identifier': '<id>'},
        related_view='.get_city',
        related_view_kwargs={'identifier': '<city.uuid>'},
        type_='city',
        schema='CitySchema',
        id_field='uuid',
        default=None
    )

    class Meta:
        type_ = 'building'
        self_view = '.get_building'
        self_view_kwargs = {'identifier': '<id>'}
        self_view_many = '.list_buildings'
        strict = True


class RoomSchema(Schema):
    id = fields.Str(attribute="uuid", dump_only=True)
    slug = fields.Str()
    name = fields.Str()

    country = Relationship(
        #self_view='.get_country',
        #self_url_kwargs={'identifier': '<id>'},
        related_view='.get_country',
        related_view_kwargs={'identifier': '<country.uuid>'},
        type_='country',
        schema='CountrySchema',
        id_field='uuid',
        default=None
    )

    city = Relationship(
        #self_view='.get_city',
        #self_url_kwargs={'identifier': '<id>'},
        related_view='.get_city',
        related_view_kwargs={'identifier': '<city.uuid>'},
        type_='city',
        schema='CitySchema',
        id_field='uuid',
        default=None
    )

    building = Relationship(
        #self_view='.get_building',
        #self_url_kwargs={'identifier': '<id>'},
        related_view='.get_building',
        related_view_kwargs={'identifier': '<building.uuid>'},
        type_='building',
        schema='BuildingSchema',
        id_field='uuid',
        default=None
    )

    class Meta:
        type_ = 'room'
        self_view = '.get_room'
        self_view_kwargs = {'identifier': '<id>'}
        self_view_many = '.list_rooms'
        strict = True
