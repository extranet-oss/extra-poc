from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect

from extranet import app


def version_tostring(version):
    string = ''
    for num in version:
        string += str(num) + '.'
    return string[:-1]


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def redirect_back(target, default, **values):
    if not target or not is_safe_url(target):
        target = url_for(default, **values)
    return redirect(target)


def external_url(url):
    # forcing https but fuck that
    return f"https://{app.config['DOMAIN']}{url}"
