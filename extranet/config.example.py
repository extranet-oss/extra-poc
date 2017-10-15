# session
SECRET_KEY = 'Generate a 32char random string'
SESSION_COOKIE_NAME = 'extranet_session'

# database configuration
SQLALCHEMY_DATABASE_URI = 'Database url'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# office 365 oauth config
OFFICE365_CLIENT_ID = 'App ID / Client Id'
OFFICE365_CLIENT_SECRET = 'Password'
OFFICE365_DOMAIN = 'Domain'
OFFICE365_ORGANIZATIONS = [
  'Organization ID'
]