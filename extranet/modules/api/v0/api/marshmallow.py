from werkzeug.routing import BuildError
from marshmallow_jsonapi.flask import Schema as DefaultSchema, SchemaOpts, Relationship as GenericRelationship
from marshmallow_jsonapi.utils import resolve_params

from .utils import api_url


class Schema(DefaultSchema):

    def generate_url(self, view_name, **kwargs):
        return api_url(view_name, **kwargs) if view_name else None


class Relationship(GenericRelationship):

    def get_url(self, obj, view_name, view_kwargs):
        if view_name:
            kwargs = resolve_params(obj, view_kwargs, default=self.default)
            kwargs['endpoint'] = view_name
            try:
                return api_url(**kwargs)
            except BuildError:
                if None in kwargs.values():  # most likely to be caused by empty relationship
                    return None
                raise
        return None
