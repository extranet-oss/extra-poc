from flask import has_request_context, _request_ctx_stack, url_for
from werkzeug.local import LocalProxy

from extranet.utils import external_url

auth = LocalProxy(lambda: _get_auth())

default_auth_data = {
    'user': None,
    'client': None,
    'type': 'anonymous',
    'scopes': None,
    'error': None
}

def _get_auth():
    if has_request_context() and not hasattr(_request_ctx_stack.top, 'api_auth'):
        return default_auth_data

    return getattr(_request_ctx_stack.top, 'api_auth', None)


def api_url(endpoint, **kwargs):
    return external_url(url_for(f'.{endpoint}', **kwargs))
