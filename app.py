#!/usr/bin/env python3
from flask import Flask, session, request, render_template, redirect

import core

app = Flask(__name__)

# This is a temporary hardcoded """"secret"""" key, straight from flask examples
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login/office365/')
def login_office365_start():
  authorization_url, state = core.office365.authorization_url()

  session['office365.state'] = state;

  return redirect(authorization_url)

@app.route('/login/office365/auth/')
def login_office365_verify():
  if not request.args.get('code'):
    return request.args.get('error')

  if 'office365.state' not in session or session['office365.state'] != request.args.get('state'):
    return "invalid state"

  token = core.office365.fetch_token(request.args.get('code'))

  data = {
    'me': core.office365.get_from_graph('/me').json(),
    'organization': core.office365.get_from_graph('/organization').json()
  }

  for organization in data['organization']['value']:
    if organization['id'] in core.office365.ORGANIZATIONS:
      return "OK, you're from Epitech."
  return "FAIL, you're not from Epitech"