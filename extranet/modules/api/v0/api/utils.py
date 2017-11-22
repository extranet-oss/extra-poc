from flask import has_request_context, _request_ctx_stack
from werkzeug.local import LocalProxy

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
