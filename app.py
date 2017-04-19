#!/usr/bin/env python3
import bottle
from beaker.middleware import SessionMiddleware
import logging

import core

session_opts = {
  'session.type': 'file',
  'session.cookie_expires': 60 * 60 * 24 * 30,
  'session.data_dir': './data',
  'session.auto': True
}

app = application = bottle.Bottle()
wsgi_app = SessionMiddleware(app, session_opts)

@app.route('/static/<filename:path>')
def static(filename):
    return bottle.static_file(filename, root='./static')

@app.route('/')
@bottle.view('index')
def index():
  return {}

@app.route('/login/office365/')
def login_office365_start():
  session = bottle.request.environ.get('beaker.session')
  authorization_url, state = core.office365.authorization_url()

  session['office365.state'] = state;
  session.save()

  bottle.redirect(authorization_url)
  return "Redirecting..."

@app.route('/login/office365/auth/')
def login_office365_verify():
  session = bottle.request.environ.get('beaker.session')

  if not bottle.request.query.code:
    return bottle.request.query.error

  if 'office365.state' not in session or session['office365.state'] != bottle.request.query.state:
    return "invalid state"

  token = core.office365.fetch_token(bottle.request.query.code)
  return core.office365.get_from_graph('/me', token).json()

if __name__ == "__main__":
  logging.getLogger().setLevel(logging.DEBUG)
  bottle.run(app=wsgi_app, host='0.0.0.0', port=8080)
