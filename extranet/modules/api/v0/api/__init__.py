from flask import jsonify, g, url_for, request, _request_ctx_stack, make_response
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from slugify import slugify
from jose import jwt, JWTError
from base64 import urlsafe_b64decode
import binascii
import re
from functools import wraps

from extranet import app, db
from extranet.models.user import User
from extranet.models.oauth import OauthApp, OauthToken
from extranet.connections.extranet import provider
from extranet.utils import external_url
from .utils import default_auth_data

jwt_regex = re.compile('^[a-zA-Z0-9\\-_]+?\\.[a-zA-Z0-9\\-_]+?\\.[a-zA-Z0-9\\-_]+?$')

class Api():

    media_type = 'application/vnd.api+json'

    def __init__(self, blueprint=None, limiter=None):
        self._blueprint = None
        self._limiter = None

        if blueprint is not None:
            self.init_blueprint(blueprint)

        if limiter is not None:
            self.init_limiter(limiter)

    def init_blueprint(self, blueprint):
        self._blueprint = blueprint
        self.name = f'{app.config["DOMAIN"]}:{blueprint.name}'

        CORS(blueprint, origins='*', send_wildcard=True)

    def init_limiter(self, limiter):
        self._limiter = limiter

        limiter.shared_limit(app.config['RATELIMIT_API'], self.name, key_func=self._limiter_key_func)(self._blueprint)

    # getting client_id from authorization. should be fast without verification
    def _limiter_key_func(self):
        valid, data = self.verify_authentication()
        if valid:
            if data['type'] == 'user':
                return f'user:{data["user"].uuid}'
            elif data['type'] == 'basic_client' or data['type'] == 'oauth_client':
                return f'client:{data["client"].client_id}'

        return get_remote_address()

    def get(self, rule, **options):
        def decorator(f):
            options['method'] = 'GET'
            self.endpoint(rule, f, **options)
            return f
        return decorator

    def post(self, rule, **options):
        def decorator(f):
            options['method'] = 'POST'
            self.endpoint(rule, f, **options)
            return f
        return decorator

    def put(self, rule, **options):
        def decorator(f):
            options['method'] = 'PUT'
            self.endpoint(rule, f, **options)
            return f
        return decorator

    def patch(self, rule, **options):
        def decorator(f):
            options['method'] = 'PATCH'
            self.endpoint(rule, f, **options)
            return f
        return decorator

    def delete(self, rule, **options):
        def decorator(f):
            options['method'] = 'DELETE'
            self.endpoint(rule, f, **options)
            return f
        return decorator

    def endpoint(self, rule, func, method='GET', view=None, auth=True, scopes=None):

        endpoint_func = self.make_endpoint_func(func, auth, scopes)

        route_options = {
            'methods': [method]
        }
        self._blueprint.add_url_rule(rule, view, endpoint_func, **route_options)

    def make_endpoint_func(self, func, auth=True, scopes=None):
        @wraps(func)
        def endpoint_func(*args, **kwargs):
            # check request headers validity
            if 'Content-Type' in request.headers and request.headers['Content-Type'].strip() != self.media_type:
                # 415 Unsupported Media Type
                return self.make_response({'errors':[{'title': 'Unsupported Media Type'}]}, 415)

            if 'Accept' in request.headers:
                for media in request.headers['Accept'].split(','):
                    if self.media_type in media and media.strip() != self.media_type:
                        # 406 Not Acceptable
                        return self.make_response({'errors':[{'title': 'Not Acceptable'}]}, 406)

            # Check authentication if needed
            if auth:
                valid, req = self.verify_authentication(scopes)

                if not valid:
                    return self.make_response({'errors':[{'title': 'Unauthorized'}]}, 401)

                _request_ctx_stack.top.api_auth = req

            # call view func
            output = func(*args, **kwargs)
            data = output
            code = 200

            if isinstance(output, tuple):
                try:
                    data, code = output
                except ValueError:
                    pass

            # return formatted jsonapi response
            return self.make_response(data, code)
        return endpoint_func

    def make_response(self, data, code=200):
        resp = make_response(jsonify(self.normalize_jsonapi_data(data)), code)
        resp.headers['Content-Type'] = self.media_type
        return resp

    def verify_authentication(self, scopes=None):
        authorization = request.headers.get('Authorization')
        data = default_auth_data

        if authorization:
            auth_type, token = authorization.split(' ', maxsplit=1)

            # basic auth: client_id:client_secret as base64
            if auth_type == 'Basic':
                if scopes != None:
                    return False, data

                try:
                    token = urlsafe_b64decode(token).decode()
                except binascii.Error:
                    return False, data

                app_id, app_secret = token.split(':', maxsplit=1)
                client = OauthApp.query.filter_by(client_id=app_id, client_secret=app_secret).first()

                if client is not None:
                    data['client'] = client
                    data['type'] = 'basic_client'
                    return True, data

            elif auth_type == 'Bearer':
                # jwt auth: user token with all scopes
                if jwt_regex.match(token) is not None:
                    try:
                        token_data = jwt.decode(token, app.config['SECRET_KEY'],
                                                algorithms='HS256', audience=app.config['DOMAIN'], issuer=self.name)
                    except JWTError:
                        return False, data

                    user = User.query.filter_by(uuid=token_data['sub']).first()

                    if user is not None and user.registered:
                        if not user.active:
                            data['error'] = 'Account suspended'
                            return False, data

                        data['user'] = user
                        data['type'] = 'user'
                        data['scopes'] = 'all'
                        return True, data

                # default oauth bearer token auth: client access to user data
                else:
                    valid, token_data = provider.verify_request(scopes)

                    if valid:
                        data['user'] = token_data.user
                        data['client'] = token_data.client
                        data['type'] = 'oauth_client'
                        data['scopes'] = token_data.scopes
                        return True, data

        return False, data

    def normalize_jsonapi_data(self, data):

        data['jsonapi'] = {
            'version': '1.0'
        }
        if 'meta' not in data:
            data['meta'] = {}

        # set data field to null by default
        if 'data' not in data and 'errors' not in data:
            data['data'] = None

        # if limiter, send limits in meta field
        if self._limiter is not None:
            data['meta']['rate_limit'] = None

            current_limit = getattr(g, 'view_rate_limit', None)
            if current_limit:
                window_stats = self._limiter.limiter.get_window_stats(*current_limit)
                reset_in = 1 + window_stats[0]
                data['meta']['rate_limit'] = {
                    'limit': current_limit[0].amount,
                    'remaining': window_stats[1],
                    'reset': reset_in
                }

        return data

    def url_for(self, view, **kwargs):
        return external_url(url_for(f'.{view}', **kwargs))
