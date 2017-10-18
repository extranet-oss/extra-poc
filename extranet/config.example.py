# session
SECRET_KEY = 'Generate a 32char random string'
SESSION_COOKIE_NAME = 'extranet_session'
SESSION_COOKIE_HTTPONLY = True
SESSION_PROTECTION = 'basic'
REMEMBER_COOKIE_NAME = 'extranet_remember'
REMEMBER_COOKIE_HTTPONLY = True

# database configuration
SQLALCHEMY_DATABASE_URI = 'Database url'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# office 365 oauth config
OFFICE365_CONSUMER_KEY = 'App ID / Client Id'
OFFICE365_CONSUMER_SECRET = 'Password'
OFFICE365_DOMAIN = 'Domain'
OFFICE365_ORGANIZATIONS = [
  'Organization ID'
]