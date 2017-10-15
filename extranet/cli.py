from extranet import app, db

@app.cli.command('createdb')
def createdb():
  print('Creating database...')
  db.create_all()
  print('Done.')

@app.cli.command('dropdb')
def dropdb():
  print('Dropping database...')
  db.drop_all()
  print('Done.')